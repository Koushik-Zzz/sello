"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Send } from "lucide-react";
import { editProduct, getProductStatus } from "@/lib/product-api";
import { ProductState } from "@/lib/product-types";

interface AIChatPanelProps {
  productState: ProductState | null;
  isEditInProgress: boolean;
  onEditStart: () => void;
  onEditComplete: () => Promise<void>;
  onEditError: (error: Error) => void;
}

export function AIChatPanel({
  productState,
  isEditInProgress,
  onEditStart,
  onEditComplete,
  onEditError,
}: AIChatPanelProps) {
  const [prompt, setPrompt] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Basic chat history purely local for UI visualization
  type Message = { role: "user" | "assistant"; content: string; isError?: boolean };
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "How would you like to edit your 3D product?" }
  ]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isEditInProgress]);

  const handleSubmit = async () => {
    if (!prompt.trim() || isEditInProgress) return;
    
    const userPrompt = prompt.trim();
    setPrompt("");
    setMessages(prev => [...prev, { role: "user", content: userPrompt }]);
    
    onEditStart();
    
    try {
      await editProduct(userPrompt);
      
      // Poll for completion
      const POLL_INTERVAL = 2000;
      const MAX_POLLS = 150; // 5 minutes max
      let polls = 0;
      
      while (polls < MAX_POLLS) {
        const status = await getProductStatus();
        if (status.status === "complete") {
          setMessages(prev => [...prev, { role: "assistant", content: "Update complete! Here is your new 3D model." }]);
          await onEditComplete();
          return;
        } else if (status.status === "error") {
          throw new Error(status.error || "Generation encountered an error.");
        }
        await new Promise(r => setTimeout(r, POLL_INTERVAL));
        polls++;
      }
      throw new Error("Timeout waiting for edit to complete.");
    } catch (error: any) {
      console.error(error);
      setMessages(prev => [...prev, { role: "assistant", content: String(error.message || "Failed to update model"), isError: true }]);
      onEditError(error);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((msg, i) => (
          <div key={i} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
            <div 
              className={`max-w-[85%] rounded-lg px-4 py-2 ${
                msg.role === "user" 
                ? "bg-primary text-primary-foreground font-medium border-2 border-black" 
                : msg.isError 
                  ? "bg-destructive text-destructive-foreground border-2 border-black" 
                  : "bg-muted border-2 border-amber-900 border-opacity-20"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        
        {isEditInProgress && (
          <div className="flex items-start">
            <div className="bg-muted border-2 border-amber-900 border-opacity-20 rounded-lg px-4 py-2 flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Editing 3D model...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="relative mt-auto pt-2 shrink-0">
        <Textarea
          placeholder="Describe how to change the product..."
          className="min-h-[80px] resize-none pr-12 border-2 border-black focus-visible:ring-1 focus-visible:ring-black focus-visible:ring-offset-0"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isEditInProgress}
        />
        <Button 
          size="icon" 
          className="absolute bottom-2 right-2 border-2 border-black disabled:opacity-50"
          disabled={!prompt.trim() || isEditInProgress}
          onClick={handleSubmit}
        >
          {isEditInProgress ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </Button>
      </div>
    </div>
  );
}
