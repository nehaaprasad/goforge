import { ProductWorkbench } from "./product-workbench";

export function DemoPreviewSection() {
  return (
    <section
      id="demo"
      className="mx-auto w-full max-w-6xl scroll-mt-24 px-4 py-20 sm:px-6"
    >
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
          See the workflow in action
        </h2>
        <p className="mt-3 text-pretty text-zinc-400">
          The same three-panel layout your team uses to review: steps, diff, and
          live reasoning—here wired to a local sandbox repo for fast iteration.
        </p>
      </div>

      <div className="relative mt-12 flex justify-center">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_center,_rgb(99_102_241_/_0.12),_transparent_65%)]"
        />
        <ProductWorkbench variant="showcase" />
      </div>
    </section>
  );
}
