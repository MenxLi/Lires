
<script setup lang="ts">
    import type { ArxivArticle } from './arxivUtils.ts';
    import { ServerConn } from '../core/serverConn';

    const props = defineProps<{
        article: ArxivArticle,
    }>()

    function addToRBM(){
        const arxivId = props.article.id;
        new ServerConn().addArxivPaperByID(
                arxivId,
            ).then(
            ()=>{window.alert(`success: ${arxivId}`)},
            ()=>{window.alert(`failed: ${arxivId}, check log for details`)},
        )
    }

</script>

<template>
    <div id="main">
        <div class="articleBlock">
            <div class="titleBlock">
                <h2>{{ props.article.title }}</h2>
                <label class="titleId">{{ props.article.id }}</label>
            </div>
            <div class="authors">
                <label>[Authors] </label>
                <span v-for="(author, index) in props.article.authors" class="authorSpan">
                    <a :href="`https://arxiv.org/search/?query=${author}&searchtype=author`">{{ author }}</a>
                    <span v-if="index < props.article.authors.length - 1">, </span>
                </span>
            </div>
            <div class="actions">
                <a :href="`https://arxiv.org/abs/${article.id}`">Arxiv</a>
                <a :href="`https://arxiv.org/pdf/${article.id}.pdf`">PDF</a>
                <a href="#" @click="addToRBM">Add2RBM</a>
            </div>
            <p>Published: {{ props.article.publishedTime }}</p>
            <details>
                <summary>Abstract</summary>
                <p>{{ props.article.abstract }}</p>
            </details>

            <div class="sep"></div>
        </div>
    </div>
</template>

<style scoped>
    div#main{
        display: flex;
        align-items: center;
        padding: 1em;
    }
    .articleBlock{
        max-width: 1200px;
        width: 98vw;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        text-align: justify;
        gap: 0.3em;
    }
    div.titleBlock{
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.25em;
    }
    label.titleId{
        color: rgba(26, 196, 208, 0.789);
    }
    span.authorSpan{
        display: inline-block;
        padding-left: 0.25em;
        padding-right: 0.25em;
    }
    div.actions{
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        gap: 1em;
    }

    div.sep{
        width: 100%;
        justify-self: center;
        height: 0.1em;
        background-color: var(--color-border);
    }
</style>
    
