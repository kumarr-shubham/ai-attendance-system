from supabase import create_client, Client

SUPABASE_URL = "https://zpsuqzmwrtptdrdniuxc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpwc3Vxem13cnRwdGRyZG5pdXhjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcyNzk3MTksImV4cCI6MjA5Mjg1NTcxOX0.-L-112B-GEhXiHsOvIFRCVfutm6p-3VFVCpoBhQSjuo"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)