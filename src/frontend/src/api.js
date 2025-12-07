const API_URL = 'http://localhost:8000';

export async function checkHealth() {
    const res = await fetch(`${API_URL}/health`);
    return res.json();
}

export async function sendMessage(message, characterName, session_history) {
    const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, character_name: characterName, session_history })
    });
    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Request failed with status ${res.status}`);
    }
    return res.json();
}

export async function getGameState(characterName) {
    const res = await fetch(`${API_URL}/state?character_name=${characterName}`);
    return res.json();
}
