import { createMDX } from "fumadocs-mdx/next";

const withMDX = createMDX();

/** @type {import('next').NextConfig} */
const config = {
  output: "export",
  distDir: "../.pages",
  reactStrictMode: true,
  basePath: "/apx",
  assetPrefix: "/apx",
};

export default withMDX(config);
