
const path = require('path');
module.exports = {
    entry: './src/api/serverConn.ts',
    mode: 'production',
    optimization: { minimize: false, },
    output: {
        filename: 'api.js',
        path: path.resolve(__dirname, 'dist-api'),
        library: 'LiresAPI',
        libraryTarget: 'commonjs2'
    },
    resolve: {
        extensions: ['.ts', '.js', 'tsx', 'jsx'],
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                use: {
                    loader: 'ts-loader',
                    options: {
                        configFile: 'api-tsconfig.json'
                    }
                },
                exclude: /node_modules/,
            },
        ],
    },
};