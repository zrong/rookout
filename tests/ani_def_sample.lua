-- 请参照下面的格式
local data = 
{
    -- 这个 ani 定义文件中包含哪几个 plist 文件？写入 ani 中的子文件夹名称即可。支持多个文件。
    spritesheets = {"ani_misc1", "ani_misc2"},

    -- 这个 ani 定义文件中可以定义多个动画。
    animations = 
    {
        {
            -- 动画的名称。
            name = "ani_bullet_hit_magic",

            -- 每个动画帧持续多长时间，单位秒。
            delay_per_unit = 0.042,

            -- 循环次数。使用 0 代表没有动画，1 代表循环 1 次。
            loops = 1,

            -- 播放完毕后，是否显示原始的帧内容。
            restore_original_frames = false,

            -- 定义 plist 中的碎图文件名称，%2d 用于高位补零。
            frame_name = "ani_bullet_hit_magic_%02d.png",

            -- 用于替换 %02d 的序号范围。
            range = {1, 34},
        },
    }
}
return data
