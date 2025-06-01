# Source: https://github.com/K0lb3/UnityPy/blob/master/UnityPy/export/Texture2DConverter.py
import warnings

from UnityPy.enums import TextureFormat

TF = TextureFormat

def compress_etcpak(
    data: bytes, width: int, height: int, target_texture_format: TextureFormat
) -> bytes:
    import etcpak  # etcpak is imported locally in the original function

    if target_texture_format in [TF.DXT1, TF.DXT1Crunched]:
        return etcpak.compress_bc1(data, width, height)
    elif target_texture_format in [TF.DXT5, TF.DXT5Crunched]:
        return etcpak.compress_bc3(data, width, height)
    elif target_texture_format == TF.BC4:
        return etcpak.compress_bc4(data, width, height)
    elif target_texture_format == TF.BC5:
        return etcpak.compress_bc5(data, width, height)
    elif target_texture_format == TF.BC7:
        # Modified call to compress_bc7, not passing 'None' as the second argument as it does not accept it
        return etcpak.compress_bc7(data, width, height)
    elif target_texture_format in [TF.ETC_RGB4, TF.ETC_RGB4Crunched, TF.ETC_RGB4_3DS]:
        return etcpak.compress_etc1_rgb(data, width, height)
    elif target_texture_format == TF.ETC2_RGB:
        return etcpak.compress_etc2_rgb(data, width, height)
    elif target_texture_format in [TF.ETC2_RGBA8, TF.ETC2_RGBA8Crunched, TF.ETC2_RGBA1]:
        return etcpak.compress_etc2_rgba(data, width, height)
    else:
        raise NotImplementedError(
            f"etcpak has no compress function for {target_texture_format.name}"
        )


def patch_unitypy():
    # As of UnityPy 1.22.3, the compress_etcpak function has an issue with the bc7 compression,
    # as it passes `None` as the second argument to `etcpak.compress_bc7`, which is not supported.
    # (even though it should be supported according to the etcpak documentation)
    try:
        from UnityPy.export import Texture2DConverter

        Texture2DConverter.compress_etcpak = compress_etcpak
        print("[UNOFFICIAL RETRO PATCH] Successfully monkey patched compress_etcpak.")
    except (AttributeError, ImportError) as e:
        warnings.warn(
            f"[UNOFFICIAL RETRO PATCH] Failed to monkey patch compress_etcpak: {e}. Ensure UnityPy structure is as expected."
        )
