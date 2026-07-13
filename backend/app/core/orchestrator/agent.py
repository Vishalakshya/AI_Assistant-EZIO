import logging
import json
import time
from typing import Any, Dict, List, Optional, AsyncGenerator
from app.core.llm.base import LLMProvider
from app.core.tools.manager import ToolManager
from app.core.tools.schemas import ToolContext
from app.core.memory.context_builder import memory_builder
from app.core.orchestrator.classifier import RequestClassifier
from app.core.orchestrator.analyzer import IntentAnalyzer
from app.core.orchestrator.planner import Planner
from app.core.orchestrator.executor import ToolExecutor
from app.core.orchestrator.router import FastRouter

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Optimized Local-First AI Orchestrator.
    Bypasses LLM classification and planning using a high-speed Python router.
    Limits LLM execution to exactly one call when needed.
    """
    def __init__(self, llm_provider: LLMProvider, tool_manager: ToolManager):
        self.llm = llm_provider
        self.tools = tool_manager
        self.router = FastRouter()
        
        # Keep legacy layers for backwards-compatibility or complex fallbacks
        self.classifier = RequestClassifier(llm_provider)
        self.analyzer = IntentAnalyzer(llm_provider, tool_manager)
        self.planner = Planner(llm_provider, tool_manager)
        self.executor = ToolExecutor(tool_manager)

    async def process_message(self, user_id: str, session_id: str, message: str) -> str:
        """
        Synchronous wrapper for REST fallback compatibility.
        Aggregates streamed tokens.
        """
        tokens = []
        async for event_type, data in self.stream_message(user_id, session_id, message):
            if event_type == "token":
                tokens.append(data)
            elif event_type == "final":
                return data
        return "".join(tokens)

    async def stream_message(self, user_id: str, session_id: str, message: str) -> AsyncGenerator[tuple, None]:
        """
        Main optimized execution pipeline.
        Yields events: (event_type, data)
        """
        start_time = time.perf_counter()
        
        # 1. Fast Python Router Check
        router_start = time.perf_counter()
        route_res = self.router.route(message)
        router_latency = (time.perf_counter() - router_start) * 1000

        tool_latency = 0.0
        mem_latency = 0.0
        llm_latency = 0.0
        
        tool_latency_str = "skipped"
        mem_latency_str = "skipped"
        llm_latency_str = "skipped"

        # Check if matched directly to a tool
        if route_res:
            tool_name, tool_args, requires_llm = route_res
            yield ("thinking", f"Executing {tool_name}...")

            # Special case: Clock/Time tool
            if tool_name == "clock":
                from datetime import datetime
                now = datetime.now()
                time_str = now.strftime("%I:%M %p")
                date_str = now.strftime("%A, %B %d, %Y")
                response = f"The current time is **{time_str}** on {date_str}."
                
                total_latency = time.perf_counter() - start_time
                self._log_profile(router_latency, "skipped", "skipped", "skipped", total_latency)
                yield ("final", response)
                return

            # Execute tool immediately
            tool_start = time.perf_counter()
            context = ToolContext(user_id=user_id, session_id=session_id)
            tool_result = await self.tools.execute_tool_call(tool_name, tool_args, context)
            tool_latency = (time.perf_counter() - tool_start) * 1000
            tool_latency_str = f"{tool_latency:.1f} ms"

            if not requires_llm:
                # Deterministic tool response formatting in Python
                response = self._format_tool_response(tool_name, tool_args, tool_result)
                total_latency = time.perf_counter() - start_time
                self._log_profile(router_latency, tool_latency_str, "skipped", "skipped", total_latency)
                yield ("final", response)
                return
            else:
                # One LLM call to synthesize response
                yield ("thinking", "Synthesizing response...")
                
                system_prompt = (
                    "You are EZIO, a helpful desktop AI assistant.\n"
                    "Formulate a concise and clear natural language response summarizing the tool execution results.\n"
                    f"User Query: {message}\n"
                    f"Tool Executed: {tool_name}\n"
                    f"Result: {tool_result.output if tool_result.status == 'success' else tool_result.error_message}"
                )
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]

                llm_start = time.perf_counter()
                message_id = str(int(time.time() * 1000))
                yield ("stream_start", message_id)

                full_text = []
                async for chunk in self.llm.stream_response(messages=messages):
                    token = chunk.get("content", "")
                    if token:
                        full_text.append(token)
                        yield ("token", token)

                llm_latency = (time.perf_counter() - llm_start) * 1000
                llm_latency_str = f"{llm_latency:.1f} ms"

                total_latency = time.perf_counter() - start_time
                self._log_profile(router_latency, tool_latency_str, "skipped", llm_latency_str, total_latency)
                yield ("final", "".join(full_text))
                return

        # 2. General Conversation Fallback (Exactly One LLM Call)
        # Check if memory is actually needed (lightweight check to bypass memory retrieval)
        memory_keywords = ["remember", "you", "my", "yesterday", "project", "what did", "history", "last time"]
        needs_memory = any(kw in message.lower() for kw in memory_keywords)

        memory_context = ""
        if needs_memory:
            mem_start = time.perf_counter()
            memory_context = await memory_builder.build_context(user_id, message)
            mem_latency = (time.perf_counter() - mem_start) * 1000
            mem_latency_str = f"{mem_latency:.1f} ms"

        yield ("thinking", "Reasoning...")

        system_prompt = (
            "You are EZIO, a helpful desktop AI assistant.\n"
            "Respond to the user's message concisely."
        )
        if memory_context:
            system_prompt += f"\n\n[Memory Context]:\n{memory_context}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        llm_start = time.perf_counter()
        message_id = str(int(time.time() * 1000))
        yield ("stream_start", message_id)

        full_text = []
        async for chunk in self.llm.stream_response(messages=messages):
            token = chunk.get("content", "")
            if token:
                full_text.append(token)
                yield ("token", token)

        llm_latency = (time.perf_counter() - llm_start) * 1000
        llm_latency_str = f"{llm_latency:.1f} ms"

        total_latency = time.perf_counter() - start_time
        self._log_profile(router_latency, "skipped", mem_latency_str, llm_latency_str, total_latency)
        yield ("final", "".join(full_text))

    def _format_tool_response(self, tool_name: str, args: Dict[str, Any], tool_result: Any) -> str:
        """Helper to format deterministic tool outputs in pure Python."""
        if tool_result.status != "success":
            return f"Error executing {tool_name}: {tool_result.error_message}"

        if tool_name == "open_application":
            return f"I have opened **{args.get('app_name')}** for you."
        
        elif tool_name == "close_application":
            return f"I have closed **{args.get('app_name')}**."
        
        elif tool_name == "set_volume":
            return f"Volume set to **{args.get('level')}%**."
        
        elif tool_name == "capture_camera":
            return "Camera photo captured successfully using your webcam."

        elif tool_name == "get_system_stats":
            try:
                stats = json.loads(tool_result.output) if isinstance(tool_result.output, str) else tool_result.output
                return (
                    "Here's a summary of your computer's current status:\n\n"
                    f"* **CPU:** {stats.get('cpu', 'N/A')}% usage\n"
                    f"* **RAM:** {stats.get('ram', 'N/A')}% used\n"
                    f"* **Disk:** {stats.get('disk', 'N/A')}% utilized\n"
                    f"* **Battery:** {stats.get('battery', 'N/A')}% charge"
                )
            except Exception:
                return f"System Stats: {tool_result.output}"

        elif tool_name == "get_running_processes":
            try:
                processes = json.loads(tool_result.output) if isinstance(tool_result.output, str) else tool_result.output
                lines = ["Here are the top running processes by resource usage:\n"]
                for p in processes[:10]:
                    lines.append(f"- **{p.get('name')}** (PID: {p.get('pid')}) — CPU: {p.get('cpu_percent', 0):.1f}%, RAM: {p.get('memory_percent', 0):.1f}%")
                return "\n".join(lines)
            except Exception:
                return f"Running Processes: {tool_result.output}"

        return f"Tool {tool_name} completed successfully."

    def _log_profile(self, router_ms: float, tool_str: str, mem_str: str, llm_str: str, total_sec: float):
        """Logs a formatted profile block of the request latency."""
        logger.info(
            f"\n--- LATENCY PROFILE ---\n"
            f"Router .......... {router_ms:.2f} ms\n"
            f"Tool ............ {tool_str}\n"
            f"Memory .......... {mem_str}\n"
            f"LLM ............. {llm_str}\n"
            f"Total ........... {total_sec * 1000:.2f} ms\n"
            f"-----------------------"
        )
