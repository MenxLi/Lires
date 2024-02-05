
<script setup lang="ts">
    import EditorBlock from './editor/EditorBlock.vue';
    import { ref } from 'vue';

    const __isDev = import.meta.env.DEV;

    const text = ref<string>('');
    const preview = ref<boolean>(false);

    function saveNote() {
        console.log('Note saved');
    }

    const uploadImages = async (files: File[]) => {
        console.log('Images uploaded', files);
    }
</script>

<template>
    <div class="test" v-if="__isDev">
        <EditorBlock v-model:text="text" v-model:preview="preview" @on-save="saveNote" @on-upload-images="uploadImages"></EditorBlock>
    </div>
    <p v-else>
        Test is not available in production
    </p>
</template>