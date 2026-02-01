"use client";

import React, { forwardRef, useRef } from "react";
import Image from "next/image";

import { cn } from "@/lib/utils";
import { AnimatedBeam } from "@/components/ui/animated-beam";
import { Python } from "@/components/ui/svgs/python";
import { ReactDark } from "@/components/ui/svgs/reactDark";
import { Typescript } from "@/components/ui/svgs/typescript";
import { ShadcnUi } from "@/components/ui/svgs/shadcnUi";
import { Fastapi } from "@/components/ui/svgs/fastapi";
import { Uv } from "@/components/ui/svgs/uv";

const Circle = forwardRef<
  HTMLDivElement,
  { className?: string; children?: React.ReactNode }
>(({ className, children }, ref) => {
  return (
    <div
      ref={ref}
      className={cn(
        "z-10 flex size-12 items-center justify-center rounded-full border-2 border-border bg-background p-3 shadow-[0_0_20px_-12px_rgba(0,0,0,0.8)]",
        className,
      )}
    >
      {children}
    </div>
  );
});

Circle.displayName = "Circle";

export function ApxEcosystemDiagram() {
  const containerRef = useRef<HTMLDivElement>(null);
  const apxRef = useRef<HTMLDivElement>(null);
  const pythonRef = useRef<HTMLDivElement>(null);
  const fastapiRef = useRef<HTMLDivElement>(null);
  const uvRef = useRef<HTMLDivElement>(null);
  const reactRef = useRef<HTMLDivElement>(null);
  const typescriptRef = useRef<HTMLDivElement>(null);
  const shadcnRef = useRef<HTMLDivElement>(null);

  return (
    <div
      className="relative flex h-[400px] w-full items-center justify-center overflow-hidden rounded-lg border bg-background p-10 md:shadow-xl"
      ref={containerRef}
    >
      <div className="flex size-full max-w-3xl items-center justify-between">
        {/* Left side - Frontend technologies */}
        <div className="flex flex-col items-center justify-center gap-8">
          <Circle ref={reactRef}>
            <ReactDark className="size-6" />
          </Circle>
          <Circle ref={typescriptRef}>
            <Typescript className="size-6" />
          </Circle>
          <Circle ref={shadcnRef}>
            <ShadcnUi className="size-6" />
          </Circle>
        </div>

        {/* Center - APX */}
        <Circle ref={apxRef} className="size-20 p-4">
          <Image
            src="/apx/logo.svg"
            alt="apx"
            width={48}
            height={48}
            className="size-full"
          />
        </Circle>

        {/* Right side - Backend technologies */}
        <div className="flex flex-col items-center justify-center gap-8">
          <Circle ref={pythonRef}>
            <Python className="size-6" />
          </Circle>
          <Circle ref={fastapiRef}>
            <Fastapi className="size-6" />
          </Circle>
          <Circle ref={uvRef}>
            <Uv className="size-6" />
          </Circle>
        </div>
      </div>

      {/* Animated beams from apx to left side */}
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={apxRef}
        toRef={reactRef}
        curvature={0}
        reverse
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={apxRef}
        toRef={typescriptRef}
        curvature={0}
        reverse
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={apxRef}
        toRef={shadcnRef}
        curvature={0}
        reverse
      />

      {/* Animated beams from apx to right side */}
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={apxRef}
        toRef={pythonRef}
        curvature={0}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={apxRef}
        toRef={fastapiRef}
        curvature={0}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={apxRef}
        toRef={uvRef}
        curvature={0}
      />
    </div>
  );
}
