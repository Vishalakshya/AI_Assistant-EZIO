import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChatStore } from '../../stores/useChatStore';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const MarkdownRenderer = ({ content }: { content: string }) => {
  return (
    <div className="prose prose-invert prose-sm max-w-none text-zinc-200">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                style={atomDark as any}
                language={match[1]}
                PreTag="div"
                className="rounded-xl overflow-hidden my-4 text-xs shadow-xl ring-1 ring-white/10"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className="bg-zinc-800/80 rounded px-1.5 py-0.5 font-mono text-[13px] text-blue-300" {...props}>
                {children}
              </code>
            );
          },
          p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
          a: ({ children, href }) => <a href={href} className="text-blue-400 hover:text-blue-300 underline underline-offset-4 decoration-blue-500/30 transition-colors" target="_blank" rel="noreferrer">{children}</a>,
          ul: ({ children }) => <ul className="list-disc pl-5 mb-4 space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal pl-5 mb-4 space-y-1">{children}</ol>,
          h1: ({ children }) => <h1 className="text-xl font-bold mb-4 mt-6 text-white">{children}</h1>,
          h2: ({ children }) => <h2 className="text-lg font-bold mb-3 mt-5 text-white">{children}</h2>,
          h3: ({ children }) => <h3 className="text-base font-bold mb-2 mt-4 text-zinc-100">{children}</h3>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

const ToolExecutionCard = ({ tool }: { tool: { toolName: string, message: string, status: string } }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="flex flex-col space-y-2 bg-zinc-900/50 border border-zinc-800 backdrop-blur-xl rounded-2xl p-4 my-2 max-w-[85%] shadow-lg ring-1 ring-white/5"
    >
      <div className="flex items-center space-x-3">
        <div className="relative flex items-center justify-center w-8 h-8 bg-zinc-800 rounded-lg shadow-inner">
          <div className="absolute inset-0 rounded-lg ring-1 ring-inset ring-white/10"></div>
          {tool.status === 'running' ? (
            <div className="w-4 h-4 rounded-full border-2 border-zinc-600 border-t-blue-500 animate-spin" />
          ) : (
            <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </div>
        <div>
          <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">{tool.toolName}</h4>
          <p className="text-sm text-zinc-200 mt-0.5">{tool.message}</p>
        </div>
      </div>
    </motion.div>
  );
};

const ChatWindow: React.FC = () => {
  const messages = useChatStore(state => state.messages);
  const isThinking = useChatStore(state => state.isThinking);
  const activeTools = useChatStore(state => state.activeTools);
  
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, activeTools, isThinking]);

  return (
    <div className="flex flex-col h-full w-full max-w-4xl mx-auto px-6 pb-32">
      <div className="flex-1 overflow-y-auto pt-10 pb-4 space-y-8 scrollbar-hide">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
              className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div 
                className={`max-w-[85%] rounded-3xl px-6 py-4 shadow-xl ${
                  msg.role === 'user' 
                    ? 'bg-gradient-to-tr from-blue-600 to-blue-500 text-white rounded-br-sm' 
                    : 'bg-zinc-900/80 backdrop-blur-2xl border border-zinc-800/80 text-zinc-100 rounded-bl-sm ring-1 ring-white/5'
                }`}
              >
                {msg.role === 'user' ? (
                  <p className="text-[15px] leading-relaxed font-medium">{msg.content}</p>
                ) : (
                  <MarkdownRenderer content={msg.content} />
                )}
              </div>
            </motion.div>
          ))}
          
          {activeTools.map((tool, idx) => (
            <ToolExecutionCard key={`tool-${idx}`} tool={tool} />
          ))}
          
          {isThinking && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center space-x-3 bg-zinc-900/60 backdrop-blur-xl border border-zinc-800/50 rounded-2xl px-5 py-3 w-fit shadow-lg ml-2"
            >
              <div className="flex space-x-1.5 items-center">
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-1.5 h-1.5 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
              <span className="text-sm font-medium text-zinc-400 bg-clip-text text-transparent bg-gradient-to-r from-zinc-400 to-zinc-500">EZIO is reasoning...</span>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={bottomRef} className="h-4" />
      </div>
    </div>
  );
};

export default ChatWindow;
