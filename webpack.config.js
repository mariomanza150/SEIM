const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
  mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
  entry: {
    dashboard: './static/js/dashboard.js',
    applications: './static/js/applications.js',
    programs: './static/js/programs.js',
    documents: './static/js/documents.js',
    auth_entry: './static/js/auth_entry.js',
  },
  output: {
    path: path.resolve(__dirname, 'static/dist'),
    filename: '[name].[contenthash].js',
    publicPath: '/static/dist/',
    clean: true,
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
          },
        },
      },
      {
        test: /\.css$/i,
        use: [MiniCssExtractPlugin.loader, 'css-loader'],
      },
    ],
  },
  plugins: [
    new CleanWebpackPlugin(),
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash].css',
    }),
    // Bundle analyzer (only in development or when explicitly enabled)
    ...(process.env.ANALYZE ? [new BundleAnalyzerPlugin()] : []),
    // Compression plugin for production
    ...(process.env.NODE_ENV === 'production' ? [
      new CompressionPlugin({
        test: /\.(js|css|html|svg)$/,
        algorithm: 'gzip',
        threshold: 10240,
        minRatio: 0.8,
      }),
    ] : []),
  ],
  optimization: {
    splitChunks: {
      chunks: 'all',
      maxInitialRequests: 10,
      maxAsyncRequests: 10,
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10,
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          priority: 5,
        },
        modules: {
          test: /[\\/]static[\\/]js[\\/]modules[\\/]/,
          name: 'modules',
          chunks: 'all',
          priority: 8,
        },
        performance: {
          test: /[\\/]static[\\/]js[\\/]modules[\\/](performance|api-enhanced|dynamic-loader)\.js$/,
          name: 'performance',
          chunks: 'all',
          priority: 9,
        },
      },
    },
    runtimeChunk: 'single',
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: process.env.NODE_ENV === 'production',
            drop_debugger: process.env.NODE_ENV === 'production',
          },
          mangle: true,
        },
        extractComments: false,
      }),
      new CssMinimizerPlugin({
        minimizerOptions: {
          preset: [
            'default',
            {
              discardComments: { removeAll: true },
              normalizeWhitespace: true,
            },
          ],
        },
      }),
    ],
    usedExports: true,
    sideEffects: false,
  },
  performance: {
    hints: 'warning',
    maxEntrypointSize: 512000,
    maxAssetSize: 512000,
  },
  devtool: process.env.NODE_ENV === 'production' ? false : 'source-map',
  resolve: {
    extensions: ['.js'],
  },
}; 