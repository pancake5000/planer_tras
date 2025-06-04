// This script expects an element with id="sse-log" and connects to the SSE endpoint.

function addLog(msg: string) {
    const log = document.getElementById('sse-log');
    if (!log) return;
    const li = document.createElement('li');
    li.textContent = msg;
    log.appendChild(li);
    log.scrollTop = log.scrollHeight;
}

function getSseUrl(): string {
    // Use the data-sse-url attribute if present
    const container = document.getElementById('sse-log-container');
    if (container && container instanceof HTMLElement && container.dataset.sseUrl) {
        return container.dataset.sseUrl;
    }
    // Fallback: use absolute path with /planer/ prefix
    return "/planer/sse/notifications/";
}

document.addEventListener("DOMContentLoaded", () => {
    const evtSource = new EventSource(getSseUrl());
    evtSource.addEventListener("newBoard", function(e: MessageEvent) {
        const data = JSON.parse(e.data);
        addLog(`Nowa plansza: "${data.board_name}" (ID: ${data.board_id}) utworzona przez ${data.creator_username}`);
    });
    evtSource.addEventListener("newPath", function(e: MessageEvent) {
        const data = JSON.parse(e.data);
        addLog(`Nowa ścieżka: "${data.path_name}" (ID: ${data.path_id}) na planszy "${data.board_name}" (ID planszy: ${data.board_id}) utworzona przez ${data.user_username}`);
    });
    evtSource.onerror = function() {
        addLog("Błąd połączenia z serwerem powiadomień.");
    };
});
