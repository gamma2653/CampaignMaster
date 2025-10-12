import { defineConfig } from '@rsbuild/core';

export default defineConfig({
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
    // All already default.
});
