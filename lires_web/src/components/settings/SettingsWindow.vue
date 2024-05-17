
<script setup lang="ts">
    import UserCard from './UserCard.vue';
    import ConfigTheme from './ConfigTheme.vue';
    import ConfigShowTags from './ConfigShowTags.vue';
    import ConfigShowHomeInfoPanel from './ConfigShowHomeInfoPanel.vue';
    import ConfigShowScatterPlot from './ConfigShowScatterPlot.vue';
    import ConfigPageCapacity from './ConfigPageCapacity.vue';

    import { useDataStore } from '@/state/store';
    const userInfo = useDataStore().user;   // is already a ref

</script>

<template>
    <div :style="{
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem',
        padding: '0.5rem',
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
        <hr>

        <ConfigTheme/>
        <ConfigPageCapacity/>
        <ConfigShowTags/>
        <ConfigShowHomeInfoPanel/>
        <ConfigShowScatterPlot/>
    </div>
</template>