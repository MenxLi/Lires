

# Enviroment variales

There are various enviroment variables that can control the behavior of the servers, listed here:

**Common variables**
Applies to all servers.
|Variable|Description|Default|
|---|---|---|
|`LRS_HOME`| The path to the directory where `Lires` stores its data. | `~/.Lires` |
|`LRS_TERM_LOG_LEVEL`| The terminal logging level. | `INFO` |
|`LRS_LOG_LEVEL`| The logging level send to the log server. | `DEBUG` |

**`lires server` variables**
|Variable|Description|Default|
|---|---|---|
|`LRS_SSL_KEYFILE`| The path to the SSL key file. (must be used with `LRS_SSL_CERTFILE`) |  |
|`LRS_SSL_CERTFILE`| The path to the SSL certificate file. |  |
|`TVDB_CACHE_DIR` | The path to the `tiny_vectordb` cache directory. | |
|`TVDB_BACKEND` | The `tiny_vectordb` backend to use, can be set to `numpy` if error occurs. | `cxx` |

**`lires ai` variables**
|Variable|Description|Default|
|---|---|---|
|`HF_HOME`| The path to the Hugging Face home directory. |  `~/.cache/huggingface` |
|`HF_ENDPONT`| The Hugging Face API endpoint. | `"https://huggingface.co"` |
|`OPENAI_API_BASE`| The OpenAI API base URL. | `"https://api.openai.com/v1` |
|`OPENAI_API_KEY`| The OpenAI API key. |  |

**Lires-web build variables**
|Variable|Description|Default|
|---|---|---|
|`VITE_MAINTAINER_NAME`| The name of the maintainer. | |
|`VITE_MAINTAINER_EMAIL`| The email of the maintainer. | |