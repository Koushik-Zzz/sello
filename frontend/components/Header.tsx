return (
  <>
    {pathname !== "/" && (
      <header className="border-b-2 border-black shrink-0 bg-background z-50">
        <div className="w-full px-4 py-3 flex items-center justify-between relative min-h-[72px]">
          
          {/* Logo */}
          <div className="flex items-center gap-4 absolute left-4 top-1/2 -translate-y-1/2 z-10">
            <Link href="/product">
              <Boxes className="w-12 h-12 cursor-pointer" />
            </Link>
          </div>

          {/* Navigation */}
          <div className="absolute right-4 top-1/2 -translate-y-1/2 z-0 flex items-center gap-3">
            {navItems.map((item) => {
              const isActive = pathname === item.path;
              const Icon = isActive ? item.icon : (item.inactiveIcon || item.icon);

              return (
                <Link key={item.path} href={item.path}>
                  <Button
                    variant="outline"
                    className={cn(
                      "h-11 transition-all duration-300 border-2 border-black overflow-hidden flex items-center justify-center gap-0",
                      isActive
                        ? "bg-secondary px-5"
                        : "bg-background hover:bg-accent hover:scale-105 hover:border-black active:scale-95 px-3"
                    )}
                  >
                    <Icon className="w-5 h-5 shrink-0" />
                    <span
                      className={cn(
                        "whitespace-nowrap font-medium overflow-hidden transition-all duration-300 ease-in-out",
                        isActive ? "max-w-[200px] opacity-100 ml-2" : "max-w-0 opacity-0 ml-0"
                      )}
                    >
                      {item.label}
                    </span>
                  </Button>
                </Link>
              );
            })}
          </div>

        </div>
      </header>
    )}
  </>
);