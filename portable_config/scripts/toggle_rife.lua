local mp = require "mp"

local rife_enabled = false

function toggle_rife()
    if rife_enabled then
        mp.command("disable-profile rife")
        mp.command("vf remove @rife") -- We have to do manual cleanup. Thanks MPV

        mp.osd_message("RIFE Interpolation: OFF", 2)
    else
        mp.command("apply-profile rife")

        mp.osd_message("RIFE Interpolation: ON", 2)
    end

    rife_enabled = not rife_enabled
end

mp.register_script_message("toggle_rife", toggle_rife)
