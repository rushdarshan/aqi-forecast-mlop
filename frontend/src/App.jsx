import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import React, { useRef, useState } from "react";
import { CityAccordion, Closing, ForecastModal, Hero, Intelligence, ModelStory, Navigation } from "./components";

gsap.registerPlugin(ScrollTrigger, useGSAP);

export default function App() {
  const root = useRef(null);
  const [forecastOpen, setForecastOpen] = useState(false);

  useGSAP(() => {
    gsap.from(".nav-shell", { y: -32, opacity: 0, duration: 0.8, ease: "power3.out" });
    gsap.from(".hero-content > *", { y: 35, opacity: 0, duration: 1, stagger: 0.11, ease: "power3.out", delay: 0.15 });
    gsap.from(".hero-visual", { y: 70, scale: 0.92, opacity: 0, duration: 1.35, ease: "power3.out", delay: 0.45 });

    gsap.utils.toArray(".section-heading, .model-intro").forEach((heading) => {
      gsap.from(heading.children, { scrollTrigger: { trigger: heading, start: "top 78%" }, y: 45, opacity: 0, stagger: 0.12, duration: 0.8, ease: "power3.out" });
    });

    gsap.utils.toArray(".visual-reveal").forEach((visual) => {
      gsap.fromTo(visual, { scale: 0.82, opacity: 0.3 }, { scale: 1, opacity: 1, ease: "none", scrollTrigger: { trigger: visual, start: "top 90%", end: "center 55%", scrub: 1 } });
      gsap.to(visual, { opacity: 0.25, filter: "brightness(.45)", ease: "none", scrollTrigger: { trigger: visual, start: "bottom 35%", end: "bottom top", scrub: 1 } });
    });

    const cards = gsap.utils.toArray(".stack-card");
    cards.forEach((card, index) => {
      gsap.fromTo(card, { y: 140, scale: 0.94 }, { y: 0, scale: 1, ease: "none", scrollTrigger: { trigger: card, start: "top 88%", end: "top 22%", scrub: 1 } });
      if (index < cards.length - 1) gsap.to(card, { scale: 0.94, opacity: 0.72, ease: "none", scrollTrigger: { trigger: cards[index + 1], start: "top 72%", end: "top 22%", scrub: 1 } });
    });
  }, { scope: root });

  return (
    <main ref={root} className="app-shell">
      <Navigation onForecast={() => setForecastOpen(true)} />
      <Hero onForecast={() => setForecastOpen(true)} />
      <Intelligence />
      <CityAccordion />
      <ModelStory />
      <Closing onForecast={() => setForecastOpen(true)} />
      <ForecastModal open={forecastOpen} onClose={() => setForecastOpen(false)} />
    </main>
  );
}
