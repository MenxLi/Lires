<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue';
import { DataPoint } from '../../core/dataClass';
import { chatStorage, type ChatMessage, type ChatSession } from '../../utils/chatStorage';
import { AiHelper } from '../../utils/aiHelper';
import { useUIStateStore, useSettingsStore } from '@/state/store';
import { MdPreview } from 'md-editor-v3';
import { ThemeMode } from '../../core/misc';

const props = defineProps<{
    datapoint: DataPoint
}>();

const messages = ref<ChatMessage[]>([]);
const currentSession = ref<ChatSession | null>(null);
const allSessions = ref<ChatSession[]>([]);
const userInput = ref('');
const enableSearch = ref(false);
const isLoading = ref(false);
const settingsStore = useSettingsStore();
const messagesContainer = ref<HTMLElement | null>(null);
const theme = ref(ThemeMode.isDarkMode()?'dark':'light' as 'dark'|'light')
const isAtBottom = ref(true);

// Helper
const aiHelper = new AiHelper(settingsStore.openaiApiKey, settingsStore.openaiApiBase);

// Watch for setting changes to update helper
watch(() => [settingsStore.openaiApiKey, settingsStore.openaiApiBase], () => {
    aiHelper.updateConfig(settingsStore.openaiApiKey, settingsStore.openaiApiBase);
});

const handleScroll = () => {
    if (!messagesContainer.value) return;
    const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value;
    // Check if user is near bottom (within 50px tolerance)
    isAtBottom.value = scrollHeight - (scrollTop + clientHeight) < 50;
};

const scrollToBottom = async (force = true) => {
    await nextTick();
    if (messagesContainer.value) {
        if (force || isAtBottom.value) {
            messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
    }
};

const loadChats = async (paperId: string) => {
    if (!paperId.trim()) return;
    const data = await chatStorage.getPaperChats(paperId);
    if (data) {
        allSessions.value = data.sessions.sort((a, b) => b.updatedAt - a.updatedAt);
        if (data.currentSessionId) {
            const sess = allSessions.value.find(s => s.id === data.currentSessionId);
            if (sess) {
                currentSession.value = sess;
                messages.value = sess.messages;
                scrollToBottom();
                return;
            }
        }
    } else {
        allSessions.value = [];
    }
    // If no session exists or was found, create a new one
    await createNewSession(paperId);
};

const createNewSession = async (paperId: string) => {
    if (!paperId.trim()) return;
    const newSession: ChatSession = {
        id: crypto.randomUUID(),
        title: `Chat ${allSessions.value.length + 1}`,
        messages: [],
        updatedAt: Date.now()
    };

    // Update local state immediately to separate UI from storage sync
    allSessions.value.unshift(newSession);
    currentSession.value = newSession;
    messages.value = newSession.messages;

    try{
        await chatStorage.saveSession(paperId, JSON.parse(JSON.stringify(newSession)));
    } catch (error) {
        useUIStateStore().showPopup('Failed to create new chat session', 'error');
        console.error("Error creating new chat session:", error);
    }
};

const switchSession = async (sessionId: string) => {
    const sess = allSessions.value.find(s => s.id === sessionId);
    if (sess) {
        currentSession.value = sess;
        messages.value = sess.messages;
        // Update current session in DB
        const data = await chatStorage.getPaperChats(props.datapoint.uid);
        if (data) {
            data.currentSessionId = sessionId;
            await chatStorage.savePaperChats(props.datapoint.uid, data);
        }
        scrollToBottom();
    }
};

const deleteSession = async (sessionId: string) => {
    if (!confirm('Delete this chat?')) return;
    await chatStorage.deleteSession(props.datapoint.uid, sessionId);
    await loadChats(props.datapoint.uid);
};

// Handle file upload and getting fileID
const getFileID = async (fileIdFromStorage: string | null): Promise<string> => {
    if (fileIdFromStorage) return fileIdFromStorage;

    try {
        useUIStateStore().showPopup('Uploading paper to AI...', 'info');
        const docUrl = props.datapoint.getRawDocURL(); 
        const response = await fetch(docUrl);
        const blob = await response.blob();
        const extension = props.datapoint.summary['file_type'];
        let mimetype = '';
        switch (extension) {
            case '.pdf':
                mimetype = 'application/pdf'; break;
            case '.html':
                mimetype = 'text/html'; break;
            default:
                mimetype = 'application/octet-stream';
        }

        const file = new File([blob], props.datapoint.uid + extension, { type: mimetype });

        return await aiHelper.uploadFile(file);
    } catch (error) {
        console.error("Error uploading file:", error);
        throw new Error("Failed to upload file to AI service");
    }
};

const sendMessage = async () => {
    if (!userInput.value.trim()) return;
    if (!settingsStore.openaiApiKey) {
        useUIStateStore().showPopup('Please set OpenAI API Key in settings', 'alert');
        return;
    }

    const content = userInput.value;
    userInput.value = '';
    
    // Add user message
    const userMsg: ChatMessage = { 
        id: crypto.randomUUID(),
        role: 'user', 
        content, 
        timestamp: Date.now() 
    };
    messages.value.push(userMsg);
    isLoading.value = true;
    scrollToBottom();

    try {
        // Load session to check for file ID
        const paperData = await chatStorage.getPaperChats(props.datapoint.uid);
        let fileId = paperData?.fileId || null;

        if (!fileId) {
            fileId = await getFileID(fileId);
            // Save fileId immediately
            await chatStorage.savePaperChats(props.datapoint.uid, { fileId });
        }

        const systemPrompt = `fileid://${fileId}`;
        
        // Prepare history for API (including current user message)
        const history = messages.value.map(m => ({ role: m.role as any, content: m.content }));
        
        // Create a placeholder for AI response
        const aiMsg: ChatMessage = { 
            id: crypto.randomUUID(),
            role: 'assistant', 
            content: '', 
            timestamp: Date.now() 
        };
        const msgIdx = messages.value.push(aiMsg) - 1;
        
        const stream = aiHelper.streamChat(history, settingsStore.openaiModelName, systemPrompt, enableSearch.value);

        for await (const chunk of stream) {
            messages.value[msgIdx].content += chunk;
            scrollToBottom(false);
        }

        // Save session after complete
        if (currentSession.value) {
            currentSession.value.messages = messages.value; // No need to deep clone here, store handles it
            currentSession.value.updatedAt = Date.now();
            await chatStorage.saveSession(props.datapoint.uid, currentSession.value);
        }

    } catch (error: any) {
        console.error("Chat error:", error);
        messages.value.push({ 
            role: 'system', 
            content: `Error: ${error.message || 'Unknown error occurred'}`, 
            timestamp: Date.now() 
        });
        useUIStateStore().showPopup('Failed to get response from AI', 'error');
    } finally {
        isLoading.value = false;
        scrollToBottom();
    }
};

const editMessage = async (msgIdx: number) => {
    const msg = messages.value[msgIdx];
    if (msg.role !== 'user') return;
    
    userInput.value = msg.content;
    // Remove this message and all subsequent messages
    messages.value = messages.value.slice(0, msgIdx);
    // Focus input
};

onMounted(async () => {
    await loadChats(props.datapoint.uid);
});

watch(() => props.datapoint.uid, async (newId) => {
    await loadChats(newId);
});

</script>

<template>
    <div class="reader-chat">
        <div class="chat-header">
            <div class="session-controls">
                <select 
                    v-if="allSessions.length > 0" 
                    :value="currentSession?.id" 
                    @change="(e) => switchSession((e.target as HTMLSelectElement).value)"
                    class="session-select"
                >
                    <option v-for="sess in allSessions" :key="sess.id" :value="sess.id">
                        {{ sess.title }} ({{ new Date(sess.updatedAt).toLocaleDateString() }})
                    </option>
                </select>
                <div class="header-btns">
                    <button class="icon-btn" @click="createNewSession(datapoint.uid)" title="New Chat" style="opacity: 1;">➕</button>
                    <button class="icon-btn" @click="currentSession && deleteSession(currentSession.id)" title="Delete Chat" :disabled="!currentSession">🗑️</button>
                </div>
            </div>
        </div>

        <div class="messages" ref="messagesContainer" @scroll="handleScroll">
            <div v-if="messages.length === 0" class="empty-state">
                Ask questions about the paper...
            </div>
            <div v-for="(msg, idx) in messages" :key="idx" :class="['message-row', msg.role]">
                <div :class="['message', msg.role]">
                    <div class="msg-content">
                        <MdPreview v-if="msg.role === 'assistant'" :modelValue="msg.content" :editorId="'preview-' + idx" :theme="theme"/>
                        <template v-else>
                            {{ msg.content }}
                            <div class="msg-actions" v-if="msg.role === 'user'">
                                <span class="edit-btn" @click="editMessage(idx)">✎ Edit</span>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
            <div v-if="isLoading && messages[messages.length-1]?.role !== 'assistant'" class="loading-indicator">
                AI is thinking...
            </div>
        </div>

        <div class="input-area">
            <div class="input-options">
                <label class="checkbox-label">
                    <input type="checkbox" v-model="enableSearch">
                    <span>Enable Search</span>
                </label>
            </div>
            <div class="input-row">
                <textarea 
                    v-model="userInput" 
                    @keydown.enter.exact.prevent="sendMessage"
                    placeholder="Ask about this paper (Ctrl+Enter to newline)..."
                    :disabled="isLoading"
                ></textarea>
                <button @click="sendMessage" :disabled="isLoading || !userInput.trim()">Send</button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.reader-chat {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: var(--color-background-soft, #f5f5f5);
    border-left: 1px solid var(--color-border, #ddd);
    font-family: sans-serif;
}

.chat-header {
    padding: 10px 15px;
    background-color: var(--color-background, #fff);
    border-bottom: 1px solid var(--color-border, #ddd);
}

.session-controls {
    display: flex;
    gap: 10px;
    align-items: center;
    width: 100%;
}

.session-select {
    flex: 1;
    padding: 4px;
    border-radius: 4px;
    border: 1px solid var(--color-border, #ddd);
    background-color: var(--color-background);
    color: var(--color-text);
}

.header-btns {
    display: flex;
    gap: 4px;
}

.icon-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.1em;
    padding: 4px;
    opacity: 0.6;
}
.icon-btn:hover { opacity: 1; }
.icon-btn:disabled { opacity: 0.2; cursor: default; }

.messages {
    flex: 1;
    overflow-y: auto;
    padding: 15px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.empty-state {
    text-align: center;
    color: var(--color-text-soft, #888);
    margin-top: 50px;
}

.message-row {
    display: flex;
    width: 100%;
}
.message-row.user { justify-content: flex-end; }
.message-row.assistant { justify-content: flex-start; }
.message-row.system { justify-content: center; }

.message {
    max-width: 95%;
    padding: 10px 12px;
    border-radius: 12px;
    line-height: 1;
    word-break: normal;
    position: relative;
    text-align: left; /* Ensure text internal alignment is left for readability */
}

.message.user {
    background-color: #007aff;
    color: white;
    border-bottom-right-radius: 2px;
    text-align: left; 
}

.message.assistant {
    background-color: var(--color-pure);
    border: 1px solid var(--color-border);
    border-bottom-left-radius: 2px;
}

.message.system {
    font-size: 0.85em;
    color: red;
    background: none;
    border: none;
    padding: 0;
}

.msg-actions {
    margin-top: 4px;
    font-size: 0.8em;
    opacity: 0.7;
    text-align: right;
    width: 100%;
}
.edit-btn {
    cursor: pointer;
    text-decoration: underline;
}
.edit-btn:hover { opacity: 1; }

.message.assistant :deep(.md-editor-preview-wrapper){
    padding: 0;
}
.message.assistant :deep(.md-editor-preview){
    color: var(--color-text);
}

.input-area {
    padding: 10px;
    background-color: var(--color-background, #fff);
    border-top: 1px solid var(--color-border, #ddd);
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.input-options {
    display: flex;
    justify-content: flex-end;
    padding: 0 4px;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.9em;
    cursor: pointer;
    user-select: none;
    color: var(--color-text);
}
.checkbox-label input {
    width: 14px;
    height: 14px;
    cursor: pointer;
}

.input-row {
    display: flex;
    gap: 10px;
    width: 100%;
}

textarea {
    flex: 1;
    height: 50px;
    resize: none;
    border: 1px solid var(--color-border, #ddd);
    border-radius: 8px;
    padding: 8px;
    font-family: inherit;
    background-color: var(--color-background);
    color: var(--color-text);
}
textarea:focus { outline: 2px solid #007aff; }

button {
    padding: 0 15px;
    background-color: #007aff;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
}
button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}
</style>
