import {
  ArchitectureSection,
  DemoPreviewSection,
  FaqSection,
  FeaturesGrid,
  FinalCta,
  HeroSection,
  HowItWorks,
  PageShell,
  SiteFooter,
  SiteHeader,
  TrustStrip,
} from "@/components/landing";

export default function Home() {
  return (
    <PageShell>
      <SiteHeader />
      <main>
        <HeroSection />
        <TrustStrip />
        <HowItWorks />
        <FeaturesGrid />
        <DemoPreviewSection />
        <ArchitectureSection />
        <FaqSection />
        <FinalCta />
      </main>
      <SiteFooter />
    </PageShell>
  );
}
