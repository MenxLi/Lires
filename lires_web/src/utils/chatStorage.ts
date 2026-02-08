
const DB_NAME = 'LiresChatDB';
const DB_VERSION = 2; // Upgraded version
const STORE_NAME = 'chats';

export interface ChatMessage {
    id?: string; // Add optional ID for editing tracking
    role: 'system' | 'user' | 'assistant';
    content: string;
    timestamp: number;
}

export interface ChatSession {
    id: string; // Unique session ID
    title: string;
    messages: ChatMessage[];
    updatedAt: number;
}

export interface PaperChatData {
    paperId: string;
    fileId: string | null;
    currentSessionId: string | null;
    sessions: ChatSession[];
}

export class ChatStorage {
    private dbPromise: Promise<IDBDatabase>;

    constructor() {
        this.dbPromise = new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onerror = (event) => {
                console.error("IndexedDB error:", event);
                reject("Database error: " + (event.target as IDBOpenDBRequest).error);
            };

            request.onsuccess = (event) => {
                resolve((event.target as IDBOpenDBRequest).result);
            };

            request.onupgradeneeded = (event) => {
                const db = (event.target as IDBOpenDBRequest).result;
                const transaction = (event.target as IDBOpenDBRequest).transaction!;
                
                if (!db.objectStoreNames.contains(STORE_NAME)) {
                    db.createObjectStore(STORE_NAME, { keyPath: "paperId" });
                } else {
                    // Migration from V1 to V2
                    // Old data: { paperId, messages, fileId, updatedAt }
                    // New data: { paperId, fileId, currentSessionId, sessions: [{id, title, messages, updatedAt}] }
                    
                    const store = transaction.objectStore(STORE_NAME);
                    const cursorRequest = store.openCursor();
                    
                    cursorRequest.onsuccess = (e) => {
                        const cursor = (e.target as IDBRequest).result;
                        if (cursor) {
                            const oldData = cursor.value;
                            // Check if it's already migrated (has sessions array)
                            if (!Array.isArray(oldData.sessions)) {
                                const newSession: ChatSession = {
                                    id: Date.now().toString(),
                                    title: 'Original Chat',
                                    messages: oldData.messages || [],
                                    updatedAt: oldData.updatedAt || Date.now()
                                };
                                
                                const newData: PaperChatData = {
                                    paperId: oldData.paperId,
                                    fileId: oldData.fileId || null,
                                    currentSessionId: newSession.id,
                                    sessions: [newSession]
                                };
                                cursor.update(newData);
                            }
                            cursor.continue();
                        }
                    };
                }
            };
        });
    }

    async getPaperChats(paperId: string): Promise<PaperChatData | undefined> {
        const db = await this.dbPromise;
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([STORE_NAME], "readonly");
            const objectStore = transaction.objectStore(STORE_NAME);
            const request = objectStore.get(paperId);

            request.onsuccess = (event) => {
                resolve((event.target as IDBRequest).result);
            };

            request.onerror = (event) => {
                reject((event.target as IDBRequest).error);
            };
        });
    }


    private sanitize<T>(data: T): T {
        return JSON.parse(JSON.stringify(data));
    }

    async savePaperChats(paperId: string, data: Partial<PaperChatData>) {
        const db = await this.dbPromise;
        // Merge with existing
        const existing = await this.getPaperChats(paperId);
        
        let newData: PaperChatData;
        
        if (existing) {
            newData = {
                ...existing,
                ...data,
                paperId // ensure ID
            };
        } else {
            newData = {
                paperId,
                fileId: data.fileId || null,
                currentSessionId: data.currentSessionId || null,
                sessions: data.sessions || []
            };
        }
        
        // Sanitize to remove Proxies before saving
        const plainData = this.sanitize(newData);

        return new Promise<void>((resolve, reject) => {
            const transaction = db.transaction([STORE_NAME], "readwrite");
            const objectStore = transaction.objectStore(STORE_NAME);
            const request = objectStore.put(plainData);

            request.onsuccess = () => resolve();
            request.onerror = (event) => reject((event.target as IDBRequest).error);
        });
    }
    
    async saveSession(paperId: string, session: ChatSession) {
        const data = await this.getPaperChats(paperId) || {
            paperId,
            fileId: null,
            currentSessionId: session.id,
            sessions: []
        };
        
        const idx = data.sessions.findIndex(s => s.id === session.id);
        if (idx >= 0) {
            data.sessions[idx] = session;
        } else {
            data.sessions.push(session);
        }
        data.currentSessionId = session.id;
        
        return this.savePaperChats(paperId, data);
    }
    
    async deleteSession(paperId: string, sessionId: string) {
        const data = await this.getPaperChats(paperId);
        if (!data) return;
        
        data.sessions = data.sessions.filter(s => s.id !== sessionId);
        if (data.currentSessionId === sessionId) {
            data.currentSessionId = data.sessions.length > 0 ? data.sessions[0].id : null;
        }
        
        return this.savePaperChats(paperId, data);
    }

    // Legacy method support if needed, or remove
    async getSession(paperId: string) {
        // Compatibility wrapper
        const data = await this.getPaperChats(paperId);
        if (data && data.currentSessionId) {
            const sess = data.sessions.find(s => s.id === data.currentSessionId);
            if (sess) {
                // Return structure similar to old interface but with fileId
                return {
                    messages: sess.messages,
                    fileId: data.fileId,
                    updatedAt: sess.updatedAt
                };
            }
        }
        // Return empty or new session like structure
        return undefined;
    }
}

export const chatStorage = new ChatStorage();
