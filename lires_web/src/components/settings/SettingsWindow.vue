
<script setup lang="ts">
    import UserCard from '../dashboard/UserCard.vue';
    import ConfigTheme from './ConfigTheme.vue';
    import ConfigShowTags from './ConfigShowTags.vue';

    import { useDataStore } from '../store';

    const userInfo = useDataStore().user;   // is already a ref

</script>

<template>
    <div :style="{
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        padding: '1rem',
        width: '100%',
        height: '100%',
        overflowY: 'auto',
    }">
        <div :style="{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
        }">
            <UserCard :user-info="userInfo" avatar-size="120px"/>
        </div>

        <ConfigTheme/>
        <ConfigShowTags/>
    </div>
</template>