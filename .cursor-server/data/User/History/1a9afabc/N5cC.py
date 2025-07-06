#!/usr/bin/env python3
"""
Test Dropbox token validity
"""

import dropbox
import sys

def test_dropbox_token():
    # Your Dropbox token
    token = "sl.u.AF0ZhY-38erhzFdrLPJvKAvQL3V4tFwKeK3LFCU7CIVub5KH-lBYZJje050AZ-qDY5fTqMHdMrTQOTBph2IZPNFz2tleHtAtPUR4m16XSoSaG5vFQ1GcEySeadFY7hbtZqaYyrnxmcvT2VTR35xYo2o8xAqHIlLo3qjEe71Y0mdG80Or1g3RtPKJXkIxzO9dHqrcT_Jul3gSGuljMr6rfzNYhJUQPU_PfbbhCXXMQs_IpqYa7wawSSuXtS2SLrxmoYfPFSaG5vFQ1GcEySeadFY7hbtZqaYyrnxmcvT2VTR35xYo2o8xAqHIlLo3qjEe71Y0mdG80Or1g3RtPKJXkIxzO9dHqrcT_Jul3gSGuljMr6rfzNYhJUQPU_PfbbhCXXMQs_IpqYa7wawSSuXtS2SLrxmoYfPFSaAhmKIDv4N7qale0AOHdjuh5-e8p5WDwdE_JqSJCbsSZlmGl-t0O3UsxHaMGjCoqy3MpDVYR2_XOPEWheLPrbKIwao6_2KKLrxvh--5oKlgE1NG4da1EVwGSQMK7g5rYHZkg1yEnWP5fHyLU8VOT8fdC6e5FIcKIC6HnvDmwzF0MTEnxkFGU9NQW5GULvDBTI8CFXRhg9sAK6StvwCft_uEtbpe1Piu3sG_AVd12G7R_wJggInGRWyN3SQBoGK5Lmtey5YWhTPvBXw-aqE37XYFJuC3VQl06cbVOIdrMi33YhdeoMiB3eLBCUt6H2Te619LzG_b6jixmH1nHmvyVcp4vGHUbNd8b_R8ffd2VooeX8UyDUAGZiYbSn4czgNGLoiPa_g7NG3RCeKz1JevcTbnQd_ynFhSs2eYonkIosSDy8XGuwXuLKvqPkH77NTerLNx8ogzk-Dy-a_E4XbZSSf9GrMGVOqr2NKk2yAmUoK6E4pZ_T6ZFAP6UKhJQJd0YPEHHD5sDY-2uJJccWlzVkN62qY_Z6GNVB94raiQEkxPSCea4Pcd9SxdKSmedEbXtCffKPYqp2BgEWpwfI_VcYegzO4dmu-35GwArPIWRmdHRG_WcYr9zUMo1gKapiHDDRutEY8BAgtN9BUs17an9dI20fSaKexBC4c7TQ-TxxpqOPsDOXgrKLZQrB7CXplfnlJZwb7L8LWS8LrIqmLhPp8F-WfiQSAGm-qdGCAmVmFqk_FeBGp9CTbe5dVx256JX-Bg56Napz15BohD6cZCoTlv5PpPBrHCx_tRYysd3MF4NYTuu5Zpnsjg5C9WetPGB_W1GLfh4QKPB70OCXRhCPM290VRn5rotm0t7c3_DFxI6fodsZ8R18xfFSn"
    
    try:
        print("Testing Dropbox token...")
        dbx = dropbox.Dropbox(token)
        
        # Try to get account information
        account = dbx.users_get_current_account()
        print(f"✅ Token is valid!")
        print(f"Account: {account.name.display_name}")
        print(f"Email: {account.email}")
        
        # Try to get space usage
        space_usage = dbx.users_get_space_usage()
        used = space_usage.used
        allocated = space_usage.allocation.get_individual().allocated
        
        print(f"Storage used: {used / (1024**3):.2f} GB")
        print(f"Storage allocated: {allocated / (1024**3):.2f} GB")
        print(f"Storage available: {(allocated - used) / (1024**3):.2f} GB")
        
        return True
        
    except dropbox.exceptions.AuthError as e:
        print(f"❌ Authentication error: {e}")
        print("Token is invalid or expired!")
        return False
    except dropbox.exceptions.ApiError as e:
        print(f"❌ API error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    is_valid = test_dropbox_token()
    sys.exit(0 if is_valid else 1) 