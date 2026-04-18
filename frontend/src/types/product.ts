export interface ProductSummary {
  slug: string
  name: string
  club_name?: string | null
  city?: string | null
  state?: string | null
  country?: string | null
  par?: number | null
  yardage?: number | null
  hero_image?: string | null
}

export interface ProductStats {
  total_par: number
  total_yardage: number
  tee_count: number
  holes: number
  signature_hole?: number | null
  est_round_minutes?: number | null
}

export interface ProductContent {
  headline: string
  description_html: string
  bullets: string[]
}

export interface ProductDetail extends ProductSummary {
  course_id: number
  content?: ProductContent | null
  stats?: ProductStats | null
  glass3d_url?: string | null
  patio_image?: string | null
  gallery?: string[]
}
