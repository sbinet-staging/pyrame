function void_test()
    print("inside lua void code")
    submod_setres(1,"void()")
end

function onearg_test(arg1)
    submod_setres(1,"onearg("..arg1..")")
end

function twoargs_test(arg1,arg2)
    submod_setres(1,"twoargs("..arg1..","..arg2..")")
end

function fail_test()
    submod_setres(0,"fail()")
end

function varmod_test()
    retcode,res=submod_execcmd("setvar_varmod","0","x","2")
    if retcode==0 then
        submod_setres(0,"cant setvar: %s"%(res))
    else
        submod_setres(1,"ok")
    end
end