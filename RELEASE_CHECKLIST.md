# EZIO v1.0 Release Checklist

## 1. Security & Compliance
- [ ] Verify `contextIsolation` is explicitly `true` in production builds.
- [ ] Verify `nodeIntegration` is explicitly `false` in production builds.
- [ ] Verify OpenAI API keys are successfully storing in Windows Credential Manager and NOT in plain-text SQLite.
- [ ] Confirm Tier 3 "Dangerous Actions" strictly halt execution and require explicit UI confirmation.

## 2. End-to-End Testing Smoke Tests
- [ ] Application Tools: EZIO can successfully open/close a target application (e.g., Notepad).
- [ ] System Tools: EZIO can successfully adjust master volume without crashing.
- [ ] File Tools: EZIO can recursively search for a file and summarize a PDF.
- [ ] Browser Automation: EZIO can execute a Playwright search query and extract text.

## 3. Voice & WebSockets
- [ ] Verify exponential backoff triggers gracefully when FastAPI restarts.
- [ ] Verify the `/ws/voice` pipeline successfully detects the Wake Word ("Hey EZIO").
- [ ] Verify Voice Activity Detection correctly truncates the buffer when the user stops speaking.
- [ ] Test the Hard Interrupt: Scream into the microphone while EZIO is outputting TTS to verify it immediately halts playback.

## 4. Packaging & Update Verification
- [ ] Compile the NSIS Installer using `electron-builder --win nsis`.
- [ ] Run the installer and verify the Start Menu and Desktop shortcuts are created.
- [ ] Ensure SQLite and Logs are correctly saving to `%APPDATA%/EZIO/` and not the Program Files directory.
- [ ] Test a Delta Auto-Update via `electron-updater` mocking a GitHub release.

## 5. Performance & Telemetry
- [ ] Verify React Chat UI stays strictly under 60fps frame drops even with 500+ messages loaded via Virtualization.
- [ ] Trigger an intentional fatal exception (e.g. `KeyboardInterrupt` mock) and verify it dumps successfully to `%APPDATA%/EZIO/logs/crashes/` without transmitting anything to the cloud.
