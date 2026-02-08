
import OpenAI from "openai";

export interface AIUploadParams {
    file: File;
    purpose?: "file-extract" | "fine-tune"; // Limit to likely used values
}

export type ChatRole = 'system' | 'user' | 'assistant';

export interface AIChatMessage {
    role: ChatRole;
    content: string;
}

export class AiHelper {
    private client: OpenAI | null = null;
    private apiKey: string = '';
    private baseURL: string = '';

    constructor(apiKey: string, baseURL: string) {
        this.updateConfig(apiKey, baseURL);
    }

    updateConfig(apiKey: string, baseURL: string) {
        if (this.apiKey !== apiKey || this.baseURL !== baseURL) {
            this.apiKey = apiKey;
            this.baseURL = baseURL;
            if (apiKey) {
                this.client = new OpenAI({
                    apiKey: apiKey,
                    baseURL: baseURL || undefined,
                    dangerouslyAllowBrowser: true
                });
            } else {
                this.client = null;
            }
        }
    }

    getClient(): OpenAI | null {
        return this.client;
    }

    async uploadFile(file: File, purpose: "file-extract" = "file-extract"): Promise<string> {
        if (!this.client) throw new Error("AI Client not initialized");
        
        const fileObject = await this.client.files.create({
            file: file,
            purpose: purpose as any
        });
        return fileObject.id;
    }

    async *streamChat(
        messages: AIChatMessage[], 
        model: string = "qwen-long",
        systemPrompt?: string
    ) {
        if (!this.client) throw new Error("AI Client not initialized");

        const msgList = [...messages];
        if (systemPrompt) {
            msgList.unshift({ role: 'system', content: systemPrompt });
        }

        const completion = await this.client.chat.completions.create({
            model: model,
            messages: msgList.map(m => ({ role: m.role as any, content: m.content })),
            stream: true
        });

        for await (const chunk of completion) {
            const content = chunk.choices[0]?.delta?.content || '';
            if (content) yield content;
        }
    }
}
