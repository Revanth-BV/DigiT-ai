import { createClient } from "@supabase/supabase-js";

const supabaseUrl = "https://qyuvvsdutdhvjallpzpk.supabase.co";

const supabaseKey = "sb_publishable_nUdV3tQVdZaL91a6HCjPiQ_26Bqhqra";

export const supabase = createClient(
  supabaseUrl,
  supabaseKey
);