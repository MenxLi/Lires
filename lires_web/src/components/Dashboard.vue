<script setup lang="ts">
    import Toolbar from './header/Toolbar.vue';
    import WidgetContainer from './dashboard/WidgetContainer.vue';
    import UsersWiget from './dashboard/UsersWidget.vue';
</script>

<template>
    <Toolbar />
    <div id="main-dashboard" class="slideIn">
        <WidgetContainer>
            <UsersWiget/>
        </WidgetContainer>
    </div>
</template>

<style scoped>
    div#main-dashboard{
        margin-top: calc(45px + 20px);
        display: flex;
        align-items: flex-start;
        flex-wrap: wrap;
        justify-content: center;
        flex-direction: row;
        width: calc(100vw - 20px);
        gap: 20px;
    }
</style>../api/serverConn../api/serverWebsocketConn../api/protocalT