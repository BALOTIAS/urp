# Source: https://github.com/K0lb3/UnityPy/blob/master/UnityPy/export/Texture2DConverter.py
from UnityPy.enums import TextureFormat


def compress_etcpak(
    data: bytes, width: int, height: int, target_texture_format: TextureFormat
) -> bytes:
    import etcpak  # etcpak is imported locally in the original function

    if target_texture_format in [TextureFormat.DXT1, TextureFormat.DXT1Crunched]:
        return etcpak.compress_bc1(data, width, height)
    elif target_texture_format in [TextureFormat.DXT5, TextureFormat.DXT5Crunched]:
        return etcpak.compress_bc3(data, width, height)
    elif target_texture_format == TextureFormat.BC4:
        return etcpak.compress_bc4(data, width, height)
    elif target_texture_format == TextureFormat.BC5:
        return etcpak.compress_bc5(data, width, height)
    elif target_texture_format == TextureFormat.BC7:
        # Modified call to compress_bc7, not passing 'None' as the second argument as it does not accept it
        return etcpak.compress_bc7(data, width, height)
    elif target_texture_format in [
        TextureFormat.ETC_RGB4,
        TextureFormat.ETC_RGB4Crunched,
        TextureFormat.ETC_RGB4_3DS,
    ]:
        return etcpak.compress_etc1_rgb(data, width, height)
    elif target_texture_format == TextureFormat.ETC2_RGB:
        return etcpak.compress_etc2_rgb(data, width, height)
    elif target_texture_format in [
        TextureFormat.ETC2_RGBA8,
        TextureFormat.ETC2_RGBA8Crunched,
        TextureFormat.ETC2_RGBA1,
    ]:
        return etcpak.compress_etc2_rgba(data, width, height)
    else:
        raise NotImplementedError(
            f"etcpak has no compress function for {target_texture_format.name}"
        )
