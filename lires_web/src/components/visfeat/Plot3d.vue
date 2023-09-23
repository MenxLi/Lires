
<script setup lang="ts">
    import { ref, computed, onMounted, watch } from 'vue';
    import { ThemeMode } from '../../core/misc';
    import Plotly from 'plotly.js-dist';
    import type { PlotPoints3D } from '../interface';

    const plotlyChart = ref(null as any);

    const props = defineProps<{
        data: PlotPoints3D[];
    }>();

    const pointsData = computed(() => {
        const data = props.data;
        const points = data.map((d) => {
            return {
                x: d.x,
                y: d.y,
                z: d.z,
                mode: 'markers',
                type: 'scatter3d',
                hoverinfo: 'text',
                hoverlabel: {
                    bgcolor: '#181818', // transparent background
                    font: { color: 'white' }
                },
                text: d.text,
                marker: {
                    size: 3.5,
                    opacity: d.opacity,
                    color: d.color,
                },
            };
        });
        return points;
    });

    const lightlayout = {
        // title: '3D Scatter Plot',
        autosize: true,
        margin: {
            l: 0,   // left margin
            r: 0,   // right margin
            b: 0,  // bottom margin
            t: 0,  // top margin
        },
        showlegend: false,
    };
    const darklayout = {
        ...lightlayout,
        paper_bgcolor: '#181818',
        plot_bgcolor: '#181818',
        font: {
            color: 'white'
        }
    }

    const config = {
        // Other buttons: ['zoom3d', 'pan3d', 'orbitRotation', 'tableRotation', \
        // 'handleDrag3d', 'resetCameraDefault3d', 'resetCameraLastSave3d', 'hoverClosest3d']
        modeBarButtonsToRemove: ['sendDataToCloud', 'resetCameraLastSave3d'],
        displaylogo: false,
        responsive: true,
    };

    let sceneRecord = null as any;
    function update(){
        if (!plotlyChart.value){ return; }

        // Store the camera position before the update
        const currentScene = plotlyChart.value.layout.scene;
        if (currentScene){
            sceneRecord = JSON.parse(JSON.stringify(currentScene));
        }

        Plotly.react(plotlyChart.value, pointsData.value, ThemeMode.isDarkMode()?darklayout:lightlayout, config);

        // Restore the camera position after the update
        if (currentScene && sceneRecord) {
            // plotlyChart.value.layout.scene = sceneRecord;
            Plotly.relayout(plotlyChart.value!, 'scene', sceneRecord);
            console.log("camera restored")
        }
    }
    defineExpose({update});

    onMounted(() => {
        Plotly.newPlot(plotlyChart.value!, pointsData.value, ThemeMode.isDarkMode()?darklayout:lightlayout, config);
        plotlyChart.value!.on('plotly_click', function(data: any){
            const x = data.points[0].x;
            const y = data.points[0].y;
            const z = data.points[0].z;
            const pointNumber = data.points[0].pointNumber;
            console.log(`You clicked on ${x}, ${y}, ${z} (point ${pointNumber})}`);
        });
        watch(pointsData, ()=>{
            update();
        })
    });

</script>

<template>
    <div id='plotyChart' ref="plotlyChart">
    </div>
</template>

<style scoped>
    div#plotyChart{
        width: 100%;
        height: 100%;
    }
</style>