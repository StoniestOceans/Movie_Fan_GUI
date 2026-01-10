export interface Message {
  role: 'user' | 'ai';
  content: string;
  data?: any;
  agent_used?: string;
}

export interface ChatResponse {
  response: string;
  data: any;
  agent_used: string;
}
