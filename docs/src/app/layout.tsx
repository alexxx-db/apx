import type { Metadata } from "next";
import { DM_Sans, DM_Mono } from "next/font/google";
import { Provider } from "@/components/provider";
import "./global.css";

export const metadata: Metadata = {
  title: "apx - Databricks Apps Toolkit",
  description:
    "Reliable, feature-full, human and LLM friendly development toolkit for building Databricks Apps",
  icons: {
    icon: "/apx/logo.svg",
  },
};

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
});

const dmMono = DM_Mono({
  weight: ["400", "500"],
  subsets: ["latin"],
  variable: "--font-dm-mono",
});

export default function Layout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${dmSans.variable} ${dmMono.variable}`}
      suppressHydrationWarning
    >
      <body className="flex flex-col min-h-screen font-sans">
        <Provider>{children}</Provider>
      </body>
    </html>
  );
}
