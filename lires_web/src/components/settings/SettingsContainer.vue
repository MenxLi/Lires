<template>
    <div class="settings-container">
        <div class="settings-header">
            <label>{{ title }}</label>
            <p>{{ description }}</p>
        </div>
        <div class="widget">
            <!-- Your widget component goes here -->
            <slot></slot>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        title: {
            type: String,
            required: true
        },
        description: {
            type: String,
            required: true
        }
    }
}
</script>

<style scoped>
.settings-container {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 2rem;
    min-width: 300px;
    width: 100%;

    padding-block: 0.2rem;
    padding-inline: 1rem;
    border-radius: 0.5rem;

    transition: background-color 0.15s;
}
.settings-container:hover {
    background-color: var(--color-background-lighter);
}

div.widget{
    display: flex;
    flex-grow: 0;
    align-self: 'flex-end';
    justify-self: 'flex-end';
}

.settings-header{
    text-align: left;
}

.settings-header p{
    font-size: 0.6rem;
    color: var(--color-text-soft);
    margin: 0;
    margin-top: 0.1rem;
}
</style>