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
    { id: 1, text: "Hello! I'm your AI restaurant recommender. What kind of cuisine are you in the mood for?", sender: 'ai' }
  ])
  const [input, setInput] = useState('')
  const [showRecommendation, setShowRecommendation] = useState(false)
  const [restaurant, setRestaurant] = useState(null)

  const handleSend = () => {
    if (input.trim()) {
      const newMessage = { id: messages.length + 1, text: input, sender: 'user' }
      setMessages([...messages, newMessage])
      setInput('')
      
      // Simulate AI response
      setTimeout(() => {
        const aiResponse = { id: messages.length + 2, text: "Great choice! I have the perfect Italian restaurant for you. Here's my recommendation:", sender: 'ai' }
        setMessages(prevMessages => [...prevMessages, aiResponse])
        setShowRecommendation(true)
      }, 1000)
    }
  }

  useEffect(() => {
    // Simulating API call for restaurant data
    const fetchRestaurantData = async () => {
      // Simulating API call delay
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const mockData = {
        "restaurantName": "La Bella Italia",
        "cuisine": "Italian",
        "rating": 4.7,
        "priceRange": "$$",
        "address": "123 Pasta Street, Foodville, FV 12345",
        "description": "Experience authentic Italian flavors in a cozy, rustic setting. Our handmade pasta and wood-fired pizzas will transport you straight to Italy.",
        "specialties": ["Handmade Pasta", "Wood-fired Pizza", "Tiramisu"],
        "imageUrl": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500&h=350&fit=crop",
        "openingHours": {
          "Mon-Fri": "11:00 AM - 10:00 PM",
          "Sat-Sun": "10:00 AM - 11:00 PM"
        }
      }

      setRestaurant(mockData)
    }

    if (showRecommendation) {
      fetchRestaurantData()
    }
  }, [showRecommendation])

  return (
    <Card className="w-full max-w-4xl mx-auto h-[80vh] flex flex-col shadow-lg">
      <CardHeader className="border-b">
        <CardTitle className="text-2xl font-bold">AI Restaurant Recommender</CardTitle>
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
          {showRecommendation && restaurant && (
            <div className="flex justify-start mb-4">
              <div className="flex items-end gap-2 max-w-[80%]">
                <Avatar className="w-10 h-10">
                  <AvatarFallback>AI</AvatarFallback>
                  <AvatarImage src="/ai-avatar.png" />
                </Avatar>
                <Card className="w-full max-w-sm overflow-hidden">
                  <div className="relative h-40 overflow-hidden">
                    <img 
                      src={restaurant.imageUrl} 
                      alt={restaurant.restaurantName}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-2">
                      <h2 className="text-lg font-bold text-white">{restaurant.restaurantName}</h2>
                      <p className="text-white text-sm flex items-center">
                        <Badge variant="secondary" className="mr-2">{restaurant.cuisine}</Badge>
                        <span className="flex items-center">
                          <Star className="w-3 h-3 fill-yellow-400 stroke-yellow-400 mr-1" />
                          {restaurant.rating}
                        </span>
                      </p>
                    </div>
                  </div>
                  <CardContent className="p-4">
                    <p className="text-sm text-gray-600 mb-2">{restaurant.description}</p>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="flex items-center">
                        <DollarSign className="w-4 h-4 mr-1 text-green-600" />
                        <span>{restaurant.priceRange}</span>
                      </div>
                      <div className="flex items-center">
                        <MapPin className="w-4 h-4 mr-1 text-red-600" />
                        <span>{restaurant.address}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
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