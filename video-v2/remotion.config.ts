import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

Config.overrideWebpackConfig((config) => {
  return {
    ...config,
    optimization: {
      ...config.optimization,
      concatenateModules: false,
    },
  };
});
