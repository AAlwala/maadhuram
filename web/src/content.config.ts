import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const products = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/products" }),
  schema: z.object({
    title: z.string(),
    tagline: z.string(),
    blurb: z.string(),
    size: z.string().optional(),
    badge: z.enum(["Bestseller", "New", "Gift", "Limited"]).optional(),
    image: z.string(),
    ingredients: z.array(z.string()).default([]),
    benefits: z.array(z.string()).default([]),
    variants: z
      .array(
        z.object({
          name: z.string(),
          image: z.string(),
          note: z.string().optional(),
        }),
      )
      .default([]),
    order: z.number().default(99),
  }),
});

export const collections = { products };
