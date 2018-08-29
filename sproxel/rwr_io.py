import sproxel
import os, sys


plugin_info = dict(name='RWR import')

def register():
    sproxel.register_importer(RWRImporter)
    sproxel.register_exporter(RWRExporter)

def unregister():
    sproxel.unregister_importer(RWRImporter)
    sproxel.unregister_exporter(RWRExporter)


class RWRImporter(object):
    @staticmethod
    def name(): return 'RWR model'

    @staticmethod
    def filter(): return '*.xml'

    @staticmethod
    def doImport(fn, um, prj, cur_sprite):

        voxels = list()

        # Parse the model xml file
        with open(fn, 'r') as f:
            for i, line in enumerate(f):
                # Check if the xml file is actually a model file
                if i == 0 and '<model>' not in line:
                    # This is not a model file, abort loading
                    print 'Not a RWR model file. Aborting loading.'
                    return False
                elif '</voxels>' in line:
                    break
                elif '<voxels>' in line:
                    pass
                elif '<voxel' in line:
                    # This line contains a voxel, get the data
                    x = int(line[line.find('x="')+3:line.find('"',line.find('x="')+3)])
                    y = int(line[line.find('y="')+3:line.find('"',line.find('y="')+3)])
                    z = int(line[line.find('z="')+3:line.find('"',line.find('z="')+3)])
                    r = float(line[line.find('r="')+3:line.find('"',line.find('r="')+3)])
                    g = float(line[line.find('g="')+3:line.find('"',line.find('g="')+3)])
                    b = float(line[line.find('b="')+3:line.find('"',line.find('b="')+3)])
                    a = float(line[line.find('a="')+3:line.find('"',line.find('a="')+3)])

                    # Put the data in a tuple and add it to the voxel list
                    voxels.append([x,y,z,(r,g,b,a)])

        # Sproxel does not support negative coordinates so we need to translate
        # them so they start at 0
        min_x = min(voxels,key=lambda item:item[0])[0]
        min_y = min(voxels,key=lambda item:item[1])[1]
        min_z = min(voxels,key=lambda item:item[2])[2]

        # TODO: Save the offsets to a file. They will be useful when exporting

        for voxel in voxels:
            voxel[0] -= min_x
            voxel[1] -= min_y
            voxel[2] -= min_z

        # Find the size of the model
        sizex = max(voxels,key=lambda item:item[0])[0] + 1
        sizez = max(voxels,key=lambda item:item[1])[1] + 1
        sizey = max(voxels,key=lambda item:item[2])[2] + 1

        # Make a layer and add the voxels to it
        layer = sproxel.Layer((sizex, sizez, sizey))
        for voxel in voxels:
            layer.set(*voxel)

        # Add model to the Sproxel project
        spr = sproxel.Sprite(layer)
        spr.name = os.path.splitext(os.path.basename(fn))[0]
        um.addSprite(prj, -1, spr)

        return True


class RWRExporter(object):
    @staticmethod
    def name(): return 'RWR model'

    @staticmethod
    def filter(): return '*.xml'

    @staticmethod
    def doExport(fn, prj, cur_sprite):
        if not fn.lower().endswith('.xml') : fn+='.xml'

        bounds = cur_sprite.bounds
        sizex = bounds[1][0] - bounds[0][0] + 1
        sizey = bounds[1][1] - bounds[0][1] + 1
        sizez = bounds[1][2] - bounds[0][2] + 1

        # TODO: Get the offset values

        with open(fn, 'w') as f:
            f.write('<model>\n')
            f.write('    <voxels>\n')

            # Write woxels to file
            number_of_voxels = 0
            for x in xrange(sizex):
                for z in xrange(sizez):
                    for y in xrange(sizey):
                        r,g,b,a = cur_sprite.getColor(
                            x + bounds[0][0],
                            y + bounds[0][1],
                            z + bounds[0][2])

                        if a > 0:
                            f.write('        <voxel x="' + str(x) +
                                '" y="' + str(y) + '" z="' + str(z) +
                                '" r="' + str(r) + '" g="' + str(g) +
                                '" b="' + str(b) + '" a="' + str(a) + '" />\n')
                            number_of_voxels += 1

            f.write('    </voxels>\n')
            
            f.write('    <skeleton />\n')
            f.write('    <skeletonVoxelBindings>\n')
            f.write('        <group constraintIndex="0">\n')
            for i in range(number_of_voxels):
                f.write('            <voxel index="' + str(i) + '" />\n')
            f.write('        </group>\n')
            f.write('    </skeletonVoxelBindings>\n')

            f.write('</model>\n')

        return True
