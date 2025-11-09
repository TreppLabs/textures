# Image Structure Constraints

This structure prompt is applied to ALL generated images to ensure they meet the physical requirements for laser cutting and framing.

## Physical Requirements

The generated image must be designed for laser cutting, where:
- **Black portions** will be cut out and removed, creating "voids" or "windows"
- **White portions** will remain as the solid material spanning the entire image
- The pattern must fill the entire image from **edge to edge** (top to bottom, left to right)
- **CRITICAL: The image must be a completely flat, two-dimensional pattern with no perspective, no depth, no shadows, no 3D appearance, no viewing angle, and no separate objects. It must appear as a flat graphic design filling the entire canvas.**

## Connectivity Constraints

The black portions (which become voids) must form a **connected structure** that holds the white material together. Specifically:

1. **Primary requirement**: The black pattern should connect the sides of the image within the black and white composition. The black portions should create pathways or connections that span from edge to edge.

2. **Structural integrity**: 
   - The white material (remaining after cutting) must form a single connected piece that reaches at least one edge of the image
   - It is acceptable if there are a few small black "islands" (isolated black regions) - these can be left out during cutting
   - The structure does not necessarily need to be a single continuous black pattern, as long as each white piece is solid and connects to at least one edge of the image

3. **Edge connectivity**: The design should ensure that the white material connects to the image edges (top, bottom, left, or right) to maintain structural stability. The pattern must extend all the way to the edges of the image canvas.

## Visual Guidelines

- **High contrast black and white only** (no grayscale, no intermediate tones)
- **Bold, simplified patterns** with large-scale elements
- **Minimum detail size**: All features must be at least 3-5 pixels wide. Avoid fine details, intricate textures, or tiny elements
- **Coarse, graphic style**: Think bold graphic design, not detailed illustration
- **Clean, minimal aesthetic**: Simple shapes and patterns rather than complex, detailed textures
- Patterns should create visual interest while maintaining structural connectivity
- The black voids should create an aesthetically pleasing negative space pattern
- The white material should form a cohesive, stable structure when cut
- **The pattern must fill the entire image canvas edge-to-edge with no white borders, no perspective, no depth, no shadows, no 3D effects, no viewing angles, and no separate objects. It must be a completely flat, two-dimensional graphic pattern.**

## Detail Control Instructions

To ensure laser-cutting feasibility and visual clarity:
- **Avoid**: Fine lines, intricate details, small textures, pixel-level complexity, delicate patterns
- **Prefer**: Bold shapes, large-scale patterns, simplified forms, graphic elements, clean edges
- **Style**: Think "stencil art" or "bold graphic design" rather than "detailed illustration" or "fine texture"
- **Scale**: All pattern elements should be clearly visible and substantial - nothing should be smaller than a few pixels

## Prompt Integration

This structure description should be combined with theme-specific prompts to create the final generation prompt. The structure ensures physical feasibility while the theme provides the artistic direction.

**When combining prompts, emphasize:**
- "Bold, simplified pattern"
- "Large-scale elements, no fine details"
- "Graphic, stencil-like style"
- "Minimum feature size of several pixels"
- "Avoid intricate textures or tiny details"
- "Completely flat, two-dimensional pattern with no perspective, no depth, no shadows, no 3D appearance"
- "Fill entire canvas edge-to-edge, no borders, no separate objects"

