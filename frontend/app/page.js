import ChatInterface from '../components/ChatInterface';

export default function Home() {
  return (
    <div className="flex justify-center items-center h-screen bg-gray-900">
      <div className="w-full max-w-2xl">
        <ChatInterface />
      </div>
    </div>
  );
}
