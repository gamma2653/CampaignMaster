import { defineConfig } from '@rsbuild/core';
import { pluginReact } from '@rsbuild/plugin-react';
import { tanstackRouter } from '@tanstack/router-plugin/rspack';

export default defineConfig({
    plugins: [pluginReact()],
    tools: {
        rspack: {
            plugins: [
                tanstackRouter({
                    target: 'react',
                    autoCodeSplitting: true,
                    routesDirectory: "./campaign_master/web/react/routes",
                    generatedRouteTree: "./campaign_master/web/react/routeTree.gen.ts",
                }),
            ]
        },
        // postcss: {

        // }
    },
    source: {
        entry: {
            index: './campaign_master/web/react/index.tsx',
        },
    //     tsconfigPath: 'tsconfig.json',
    },
    // output: {
    //     distPath: {
    //         root: 'dist',
    //     },
    //     target: 'web',
    // },
    // Comments are already default, and for personal reference.
});

