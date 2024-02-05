
<script setup lang="ts">
    import { watch, ref } from 'vue';
    import markdownit from 'markdown-it';
    import { FileSelectButton } from '../common/fragments';

    const props = withDefaults(defineProps<{
        preRenderFn?: (text: string) => string
        theme?: 'dark' | 'light'
    }>(), {
        theme: 'light',
        preRenderFn: (text: string) => text
    });
    const text = defineModel<string>('text', { default: '' })
    const preview = defineModel<boolean>('preview', { default: false })
    const textRender = ref(props.preRenderFn(text.value))

    watch(() => text.value, (newValue) => {
        textRender.value = markdownit().render(
            props.preRenderFn(newValue)
        )
    })

    const emit = defineEmits<{
        (evnet: 'on-input', value: string): void
        (event: 'on-save', value: string): void
        (event: 'on-upload-images', value: File[]): void
    }>();

    function onSelectUploadFile(file: File){
        emit('on-upload-images', [file])
    }

    const textarea = ref<HTMLTextAreaElement | null>(null)
    function insert(text: string){
        const start = textarea.value!.selectionStart;
        const end = textarea.value!.selectionEnd;
        const before = text.substring(0, start);
        const after = text.substring(end, text.length);
        text = before + text + after;
        textarea.value!.value = text;
    }

    defineExpose({
        insert
    })

</script>

<template>
    <div class="editor-block">
        <div class="editor-toolbar">
            <button @click="emit('on-save', text)">Save</button>
            <button @click="preview = !preview">Toggle Preview</button>
            <FileSelectButton :action="onSelectUploadFile"></FileSelectButton>
        </div>
        <div id="editor-body">
            <div id="editor-input" class="body-area" v-if="!preview">
                <textarea v-model="text" @input="emit('on-input', text)" ref="textarea"></textarea>
            </div>
            <div id="editor-preview" class="body-area" v-else>
                <div v-html="textRender"></div>
            </div>
        </div>
    </div>
</template>

<style scoped>

#editor-body{
    width: 100%;
    height: 100%;
    overflow: auto;
}

.body-area{
    width: 100%;
    height: 300px;
    padding: none;
    margin: none;
    overflow: hidden;
}

textarea{
    width: 100%;
    height: 100%;
    margin: none;
    padding: 10px;
    resize: none;
    overflow: auto;
}

</style>