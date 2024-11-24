"use client"

import { useState, useEffect } from 'react'
import { Send, Star, Clock, DollarSign, MapPin } from 'lucide-react'
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"

export default function ChatWithRecommendation() {
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      text: "Hello! I'm your Golden Retriever recommender. What kind of cuisine are you in the mood for?", 
      sender: 'ai',
      restaurant: null
    }
  ])
  const [input, setInput] = useState('')

  const fetchRestaurantRecommendation = async (userQuery) => {
    try {
      const response = await fetch('http://localhost:5000/api/json_fitter', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userQuery,
          json_schema: {
            "type": "object",
            "properties": {
              "restaurantName": { "type": "string" },
              "cuisine": { "type": "string" },
              "rating": { "type": "number" },
              "priceRange": { "type": "string" },
              "address": { "type": "string" },
              "description": { "type": "string" },
              "specialties": { "type": "array", "items": { "type": "string" } },
              "imageUrl": { "type": "string" },
              "openingHours": { "type": "object" }
            }
          }
        })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch restaurant recommendation');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching restaurant recommendation:', error);
      return null;
    }
  };

  const handleSend = async () => {
    if (input.trim()) {
      const userMessage = { 
        id: messages.length + 1, 
        text: input, 
        sender: 'user',
        restaurant: null 
      };
      setMessages([...messages, userMessage]);
      setInput('');
      
      const loadingMessage = { 
        id: messages.length + 2, 
        text: "Searching for the perfect restaurant...", 
        sender: 'ai',
        restaurant: null 
      };
      setMessages(prevMessages => [...prevMessages, loadingMessage]);

      const restaurantData = await fetchRestaurantRecommendation(input);
      
      if (restaurantData) {
        const aiResponse = { 
          id: messages.length + 3, 
          text: `I found a great ${restaurantData.cuisine} restaurant for you. Here's my recommendation:`, 
          sender: 'ai',
          restaurant: restaurantData
        };
        setMessages(prevMessages => 
          prevMessages.filter(msg => msg.id !== loadingMessage.id).concat(aiResponse)
        );
      } else {
        const errorMessage = { 
          id: messages.length + 3, 
          text: "I'm sorry, I couldn't find a restaurant recommendation at the moment. Please try again.", 
          sender: 'ai',
          restaurant: null
        };
        setMessages(prevMessages => 
          prevMessages.filter(msg => msg.id !== loadingMessage.id).concat(errorMessage)
        );
      }
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto h-[80vh] flex flex-col shadow-lg">
      <CardHeader className="border-b">
        <CardTitle className="text-2xl font-bold">Golden Retriever</CardTitle>
      </CardHeader>
      <CardContent className="flex-grow overflow-hidden p-6">
        <ScrollArea className="h-full pr-4">
          {messages.map((message) => (
            <div key={message.id} className="mb-4">
              <div className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
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
              {message.restaurant && (
                <div className="mt-4 ml-12">
                  <Card className="max-w-sm overflow-hidden">
                    <div className="relative h-40 overflow-hidden">
                      <img 
                        src={message.restaurant.imageUrl} 
                        alt={message.restaurant.restaurantName}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-2">
                        <h2 className="text-lg font-bold text-white">{message.restaurant.restaurantName}</h2>
                        <p className="text-white text-sm flex items-center">
                          <Badge variant="secondary" className="mr-2">{message.restaurant.cuisine}</Badge>
                          <span className="flex items-center">
                            <Star className="w-3 h-3 fill-yellow-400 stroke-yellow-400 mr-1" />
                            {message.restaurant.rating}
                          </span>
                        </p>
                      </div>
                    </div>
                    <CardContent className="p-4">
                      <p className="text-sm text-gray-600 mb-2">{message.restaurant.description}</p>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div className="flex items-center">
                          <DollarSign className="w-4 h-4 mr-1 text-green-600" />
                          <span>{message.restaurant.priceRange}</span>
                        </div>
                        <div className="flex items-center">
                          <MapPin className="w-4 h-4 mr-1 text-red-600" />
                          <span>{message.restaurant.address}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
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