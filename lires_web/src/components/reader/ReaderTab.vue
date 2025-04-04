<script setup lang="ts">
    import { DataPoint } from '@/core/dataClass';
    import { useRouter } from 'vue-router';
    import { useUIStateStore } from '@/state/store';

    const props = defineProps<{
        thisDatapoint: DataPoint,
        datapoints: DataPoint[],
    }>();

    const router = useRouter();
    const uiStateStore = useUIStateStore();

    function formatDataItem(item: DataPoint): string {
        const MAXLENGTH = 1000;
        let t = item.summary.year + '-' + item.summary.title;
        if (t.length > MAXLENGTH) {
            t = t.substring(0, MAXLENGTH) + '...';
        }
        return t;
    }

    const onClickItem = (dp: DataPoint) => {
        router.push( '/reader/' + dp.summary.uuid );
    };

    const onRemoveItem = (dp: DataPoint) => {
        uiStateStore.removeRecentlyReadDataUID(dp.summary.uuid);
        const index = props.datapoints.findIndex((item) => item.summary.uuid === dp.summary.uuid);
        if (index !== -1) {
            // also remove the item from the list
            // go to the first item if the current one is removed
            props.datapoints.splice(index, 1);
            if (props.thisDatapoint.summary.uuid === dp.summary.uuid) {
                if (props.datapoints.length > 0) {
                    router.push('/reader/' + props.datapoints[0].summary.uuid);
                } else {
                    router.push('/');
                }
            }
        }
    };

</script>

<template>
    <div id="reader-tab">
        <div :class="'reader-tab-item' + ( props.thisDatapoint.summary.uuid === item.summary.uuid ? ' active' : '' )"
            v-for="item in props.datapoints" :key="item.summary.uuid"
            @click="onClickItem(item)"
            :tooltip="item.summary.title"
            >
            <div class="reader-tab-item-text"> {{ formatDataItem(item) }} </div>
            <div class="reader-tab-item-close" @click.stop="onRemoveItem(item)"> </div>
        </div>
    </div>
</template>

<style scoped>
    #reader-tab {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        height: 25px;
    }

    .reader-tab-item {
        cursor: pointer;
        color: var(--color-text);
        background-color: var(--color-background);
        padding-inline: 5px;
        padding-right: 3px;
        border-radius: 3px;
        margin-inline: 5px;
        transition: all 0.2s ease-in-out;
        box-shadow: 0px 2px 2px -2px var(--color-shadow);
        user-select: none;

        display: flex;
        align-items: center;
        gap: 3px;
        max-width: 120px;
    }

    .reader-tab-item-text {
        font-size: smaller;
        font-weight: bold;
        color: var(--color-text);
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;
    }

    .reader-tab-item.active {
        background-color: var(--color-background-theme);
    }
    .reader-tab-item:hover {
        background-color: var(--color-background-theme-highlight);
    }

    .reader-tab-item:hover .reader-tab-item-close {
        opacity: 0.8;
    }
    .reader-tab-item-close {
        opacity: 0;
        cursor: pointer;
        background-color: var(--color-red);
        height: 12px;
        width: 12px;
        border-radius: 30%;
        transition: all 0.1s ease-in-out;
        box-shadow: 0px 2px 2px -1px var(--color-shadow);
        flex-shrink: 0;
    }

</style>