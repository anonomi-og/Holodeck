import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import GameStatus from './components/GameStatus';
import { sendMessage, getGameState } from './api';

const CHARACTER_NAME = "Kraven"; // Hardcoded for MVP

function App() {
  const [history, setHistory] = useState([]);
  const [gameState, setGameState] = useState(null);
  const [loading, setLoading] = useState(false);

  // Initial load
  useEffect(() => {
    refreshState();
    // Add initial greeting if history is empty
    setHistory([{ role: 'assistant', content: "Welcome to the Wailing Glacier. The cold wind bites at your face..." }]);
  }, []);

  const refreshState = async () => {
    try {
      const state = await getGameState(CHARACTER_NAME);
      setGameState(state);
    } catch (e) {
      console.error("Failed to fetch state", e);
    }
  };

  const handleSendMessage = async (text) => {
    // Optimistic user update
    const newHistory = [...history, { role: 'user', content: text }];
    setHistory(newHistory);
    setLoading(true);

    try {
      // Send to backend (convert history to format backend expects)
      // Backend expects session_history with 'role' and 'content'
      const response = await sendMessage(text, CHARACTER_NAME, newHistory);

      const assistantMsg = {
        role: 'assistant',
        content: response.narration,
        out_of_character: response.out_of_character
      };

      setHistory([...newHistory, assistantMsg]);

      if (response.updated_state) {
        setGameState(response.updated_state);
      } else {
        await refreshState();
      }
    } catch (e) {
      setHistory([...newHistory, { role: 'assistant', content: "Error: The spirits disturb the connection..." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-holodeck-dark flex items-center justify-center p-4">
      <div className="container mx-auto max-w-6xl grid grid-cols-1 md:grid-cols-3 gap-6 h-[85vh]">

        {/* Left Panel: Game State */}
        <div className="md:col-span-1 h-full">
          <GameStatus state={gameState} />
        </div>

        {/* Right Panel: Chat */}
        <div className="md:col-span-2 h-full">
          <ChatInterface
            history={history}
            onSendMessage={handleSendMessage}
            loading={loading}
          />
        </div>

      </div>
    </div>
  );
}

export default App;
