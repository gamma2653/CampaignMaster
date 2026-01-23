import { defineConfig } from '@rsbuild/core';
import { pluginReact } from '@rsbuild/plugin-react';
import { tanstackRouter } from '@tanstack/router-plugin/rspack';

// import { rspack } from '@rspack/core';
// const devMode = process.env.NODE_ENV !== "production";

export default defineConfig({
  plugins: [pluginReact()],
  tools: {
    rspack: {
      plugins: [
        tanstackRouter({
          target: 'react',
          autoCodeSplitting: true,
          routesDirectory: './campaign_master/web/react/routes',
          generatedRouteTree: './campaign_master/web/react/routeTree.gen.ts',
        }),
        // new rspack.CssExtractRspackPlugin({

        // })
      ],
      // module: {
      //     rules: [
      //         {
      //             test: /\.css$/,
      //             use: [
      //                 // First apply lightningcss, then postcss for Tailwind CSS
      //                 rspack.CssExtractRspackPlugin.loader,
      //                 {
      //                     loader: 'builtin:lightningcss-loader',
      //                     /** @type {import('@rspack/core').LightningcssLoaderOptions} */
      //                     options: {
      //                         targets: ['chrome >= 87', 'edge >= 88', '> 0.5%']
      //                     },
      //                 },
      //                 'postcss-loader',
      //             ],
      //             type: 'css',
      //         },
      //     ],
      // },
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
