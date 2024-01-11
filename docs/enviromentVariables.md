

# Enviroment variales

There are various enviroment variables that can control the behavior of the servers, listed here:

**Common variables**
Applies to all servers.
|Variable|Description|Value|
|---|---|---|
|`LRS_LOG_LEVEL`| The logging level. | `"DEBUG"`, `"INFO"` (default) ...|

**lires server variables**
|Variable|Description|Value|
|---|---|---|
|`LRS_SSL_KEYFILE`| The path to the SSL key file. (must be used with `LRS_SSL_CERTFILE`) |  |
|`LRS_SSL_CERTFILE`| The path to the SSL certificate file. |  |
|`TVDB_CACHE_DIR` | The path to the `tiny_vectordb` cache directory. | |

**lires iserver variables**
|Variable|Description|Value|
|---|---|---|
|`HF_HOME`| The path to the Hugging Face home directory. |  `~/.cache/huggingface` (default) |
|`HF_ENDPONT`| The Hugging Face API endpoint. | `"https://huggingface.co"` (default) |
|`OPENAI_API_BASE`| The OpenAI API base URL. | `"https://api.openai.com/v1` (default) |
|`OPENAI_API_KEY`| The OpenAI API key. |  |
