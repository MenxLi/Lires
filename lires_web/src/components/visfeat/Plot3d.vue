
<script setup lang="ts">
    import { ref, computed, onMounted, watch } from 'vue';
    import { ThemeMode, deepCopy } from '../../core/misc';
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
        scene: {
            xaxis: {
                title: '',
                showticklabels: false,
                tickfont: {
                    size: 10
                },
            },
            yaxis: {
                title: '',
                showticklabels: false,
                tickfont: {
                    size: 10
                },
            },
            zaxis: {
                title: '',
                showticklabels: false,
                tickfont: {
                    size: 10
                },
            },
        },
        paper_bgcolor: '#f6f6f6',
        plot_bgcolor: '#f6f6f6',
    };
    const darklayout = {
        ...lightlayout,
        paper_bgcolor: '#151515',
        plot_bgcolor: '#151515',
        font: {
            color: 'white'
        }
    }

    const config = {
        // Other buttons: ['zoom3d', 'pan3d', 'orbitRotation', 'tableRotation', \
        // 'handleDrag3d', 'resetCameraDefault3d', 'resetCameraLastSave3d', 'hoverClosest3d']
        modeBarButtonsToRemove: ['toImage', 'sendDataToCloud', 'resetCameraLastSave3d', 'resetCameraDefault3d'],
        // displayModeBar: false,
        displaylogo: false,
        responsive: true,
    };

    let cameraRecord = null as any;
    function update(){
        // BUG: somehow cannot get camera on mobile devices without using relayout event,
        //      however, the event is not triggered on touch devices with dragging.
        // maybe related to: https://github.com/plotly/plotly.js/issues/5560
        // or: https://github.com/plotly/plotly.js/issues/5698

        // TODO: a possible workaround: https://stackoverflow.com/questions/1517924/javascript-mapping-touch-events-to-mouse-events

        if (!plotlyChart.value){ return; }

        Plotly.react(plotlyChart.value, pointsData.value, ThemeMode.isDarkMode()?darklayout:lightlayout, config);

        // Restore the camera position after the update
        const currentScene = plotlyChart.value.layout.scene;
        if (currentScene && cameraRecord) {
            Plotly.relayout(plotlyChart.value!, 'scene.camera', cameraRecord);
        }
    }
    defineExpose({update});

    onMounted(() => {
        Plotly.newPlot(plotlyChart.value!, pointsData.value, ThemeMode.isDarkMode()?darklayout:lightlayout, config).then(
            () => {
                // plotlyChart.value!.on('plotly_relayouting', (e: any) =>{
                plotlyChart.value!.on('plotly_relayout', (e: any) =>{
                    console.log('plotly_relayout', e);
                    if (!e['scene.camera']){
                        // other relayout events, such as clicking on the bar
                        return;
                    }
                    const camera = e['scene.camera'];
                    cameraRecord = deepCopy(camera);
                })
            }
        )
        plotlyChart.value!.on('plotly_click', function(data: any){
            if (!data.points){ console.log('Not clicking on any data.') }
            const x = data.points[0].x;
            const y = data.points[0].y;
            const z = data.points[0].z;
            const pointNumber = data.points[0].pointNumber;
            console.log(`You clicked on ${x}, ${y}, ${z} (point ${pointNumber})}`);
        });
        watch(pointsData, ()=>{
            update();
        });
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

        overflow: hidden;
        touch-action: none;
        -ms-touch-action: none;
    }
</style>