import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { ChatMessage, ChatSession } from '../utils/chatStorage';

export interface ChatUIState {
    messages: ChatMessage[];
    currentSession: ChatSession | null;
    allSessions: ChatSession[];
    userInput: string;
    enableSearch: boolean;
    isStreaming: boolean;
}

export const useChatStateStore = defineStore('chatState', () => {
    const chatStates = ref<Record<string, ChatUIState>>({});

    return { chatStates };
});
