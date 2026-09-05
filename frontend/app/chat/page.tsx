'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const email = localStorage.getItem('user_email');
    if (!email) {
      router.push('/');
    }
  }, [router]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ message: userMsg.text }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'bot', text: data.reply }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: 'Something went wrong. Is the backend running?' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div style={{ maxWidth: '600px', margin: '50px auto', fontFamily: 'sans-serif' }}>
      <h2>Admin Chatbot</h2>
      <div style={{
        border: '1px solid #ccc',
        borderRadius: '8px',
        height: '400px',
        overflowY: 'auto',
        padding: '15px',
        marginBottom: '15px'
      }}>
        {messages.map((m, i) => (
          <div key={i} style={{
            textAlign: m.role === 'user' ? 'right' : 'left',
            margin: '8px 0'
          }}>
            <span style={{
              display: 'inline-block',
              padding: '8px 12px',
              borderRadius: '12px',
              background: m.role === 'user' ? '#0070f3' : '#eee',
              color: m.role === 'user' ? '#fff' : '#000',
              maxWidth: '80%'
            }}>
              {m.text}
            </span>
          </div>
        ))}
        {loading && <p style={{ color: '#888' }}>Thinking...</p>}
      </div>
      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder='e.g. "add the user john@xyz.com with phone +123456"'
          style={{ flex: 1, padding: '10px' }}
        />
        <button onClick={sendMessage} style={{ padding: '10px 20px' }}>
          Send
        </button>
      </div>
    </div>
  );
}