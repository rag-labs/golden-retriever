'use client'

import { useState } from 'react'
import { Send } from 'lucide-react'
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"

export default function ChatInterface() {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! How can I assist you today?", sender: 'ai' }
  ])
  const [input, setInput] = useState('')

  const handleSend = () => {
    if (input.trim()) {
      const newMessage = { id: messages.length + 1, text: input, sender: 'user' }
      setMessages([...messages, newMessage])
      setInput('')
      
      // Simulate AI response
      setTimeout(() => {
        const aiResponse = { id: messages.length + 2, text: "I'm an AI assistant. How can I help you?", sender: 'ai' }
        setMessages(prevMessages => [...prevMessages, aiResponse])
      }, 1000)
    }
  }

  return (
    <Card className="w-full max-w-4xl mx-auto h-[80vh] flex flex-col shadow-lg">
      <CardHeader className="border-b">
        <CardTitle className="text-2xl font-bold">AI Chat Assistant</CardTitle>
      </CardHeader>
      <CardContent className="flex-grow overflow-hidden p-6">
        <ScrollArea className="h-full pr-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
              <div className={`flex items-end gap-2 max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <Avatar className="w-10 h-10">
                  <AvatarFallback>{message.sender === 'user' ? 'U' : 'AI'}</AvatarFallback>
                  <AvatarImage src={message.sender === 'user' ? "/user-avatar.png" : "/ai-avatar.png"} />
                </Avatar>
                <div className={`py-3 px-4 rounded-lg ${message.sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-secondary'}`}>
                  {message.text}
                </div>
              </div>
            </div>
          ))}
        </ScrollArea>
      </CardContent>
      <CardFooter className="border-t p-4">
        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex w-full items-center space-x-2">
          <Input 
            type="text" 
            placeholder="Type your message..." 
            value={input} 
            onChange={(e) => setInput(e.target.value)}
            className="flex-grow"
          />
          <Button type="submit" size="icon" className="h-10 w-10">
            <Send className="h-5 w-5" />
            <span className="sr-only">Send</span>
          </Button>
        </form>
      </CardFooter>
    </Card>
  )
}