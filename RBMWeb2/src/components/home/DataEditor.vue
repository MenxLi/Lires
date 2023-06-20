
<script setup lang="ts">
    import { ref, computed } from 'vue';
    import { useDataStore } from '../store';
    import FloatingWindow from '../common/FloatingWindow.vue';
    import type { DataPoint } from '../../core/dataClass';

    const props = defineProps<{
        uuid: string | null,
        show: boolean,
    }>();

    const emits = defineEmits<{
        (e: "update:show", show: boolean): void
    }>();

    const show = computed({
        get: () => props.show,
        set: (newShow: boolean) => emits("update:show", newShow)
    });

    const dataStore = useDataStore();
    const datapoint = ref(null as DataPoint | null)
    if (props.uuid) { 
        datapoint.value = dataStore.database.get(props.uuid);
        if ( datapoint.value.isDummy() ){ throw new Error("DataEditor: uuid not found in database") }
    }

</script>

<template>
    <FloatingWindow v-model:show="show" :title="datapoint? datapoint.toString() : 'new'">
        NOT IMPLEMENTED YET...
    </FloatingWindow>
</template>